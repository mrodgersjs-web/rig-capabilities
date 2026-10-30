export function collect(value: string): boolean {
    return decide(value)
}

function decide(value: string): boolean {
    return Boolean(value)
}
