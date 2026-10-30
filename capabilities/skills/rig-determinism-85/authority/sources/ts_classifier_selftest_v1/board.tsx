export function render(title: string): object {
    return <div className="board">{helper(title)}</div>
}

function helper(title: string): string {
    return String(title)
}
