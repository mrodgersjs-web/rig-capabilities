import { collect } from "./worker"
import { render } from "./board"

export function execute(value: string): boolean {
    const rendered = render(value)
    return collect(rendered)
}
