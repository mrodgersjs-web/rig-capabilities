"""Local durable adapter loop. HTTP handlers never run probes or models."""
import signal
import time

from .dispatcher import Dispatcher
from .inventory import InventoryProbe
from .registry import NODE_REGISTRY


class FleetDaemon:
    def __init__(self, store, interval=2, inventory_interval=120):
        self.store, self.interval, self.inventory_interval = store, interval, inventory_interval
        self.running, self.next_inventory = True, 0

    def stop(self, *_): self.running = False

    def inventory(self):
        probe = InventoryProbe()
        for node in NODE_REGISTRY:
            try: self.store.record_inventory(node, probe.collect(node))
            except Exception as error: self.store.record_inventory_failure(node, 'Inventory probe failed: '+str(error))
        self.next_inventory = time.monotonic() + self.inventory_interval

    def cycle(self):
        if self.store.consume_inventory_refresh() or time.monotonic() >= self.next_inventory: self.inventory()
        dispatcher = Dispatcher(self.store)
        for job in self.store.list_jobs(200):
            if job['state'] == 'running': dispatcher.refresh(job)
        for _ in range(3):
            if dispatcher.launch_one() is None: break

    def run(self):
        signal.signal(signal.SIGTERM, self.stop); signal.signal(signal.SIGINT, self.stop)
        while self.running:
            self.cycle()
            if self.running: time.sleep(self.interval)

