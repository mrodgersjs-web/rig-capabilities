#!/bin/bash
# bounded_run.sh SECONDS CMD [ARGS...]
# Run CMD for at most SECONDS, then SIGTERM it, then SIGKILL 5 s later; exit with CMD's exit code.
#
# Why this exists (AS-19, 2026-09-28): the Aside sandbox refuses to signal a process that an
# earlier tool call started ("Operation not permitted"), so every server started for a proof
# must carry its own stop. The earlier pattern `perl -e 'alarm shift; exec @ARGV' N CMD` only
# works for programs that die on SIGALRM: Go programs (the temporal CLI dev server) catch and
# ignore SIGALRM, so three Temporal dev servers outlived their proofs. Here perl stays the
# parent, owns the timer, and sends SIGTERM (which Go, Node, Python and the JVM all honour).
# Usage: bounded_run.sh 100 temporal server start-dev --port 4350 --ui-port 4351 &
[ "$#" -ge 2 ] || { echo "usage: bounded_run.sh SECONDS CMD [ARGS...]" >&2; exit 2; }
exec perl -MPOSIX=:sys_wait_h -e '
  my $n = shift;
  die "bounded_run: SECONDS must be a positive integer\n" unless $n =~ /^[1-9][0-9]*$/;
  my $pid = fork; die "bounded_run: fork: $!\n" unless defined $pid;
  if (!$pid) { exec { $ARGV[0] } @ARGV or die "bounded_run: exec $ARGV[0]: $!\n" }
  my ($reaped, $st) = (0, 0);
  $SIG{ALRM} = sub {
    kill TERM => $pid;
    for (1 .. 50) {                     # up to 5 s for a clean exit, then SIGKILL
      if (waitpid($pid, WNOHANG) == $pid) { ($reaped, $st) = (1, $?); return }
      select(undef, undef, undef, 0.1);
    }
    kill KILL => $pid;
  };
  alarm $n;
  until ($reaped) {
    my $r = waitpid($pid, 0);
    if ($r == $pid) { $st = $?; last }
    last if $r == -1 && !$!{EINTR};
  }
  exit($st & 127 ? 128 + ($st & 127) : $st >> 8);
' "$@"
