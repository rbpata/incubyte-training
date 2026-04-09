import {initialItems} from './utils';
import React, {useMemo} from 'react';
export function Index() {
    const [count, setCount] = React.useState(0);
    const [items] = React.useState(initialItems);
    const selectedItem = useMemo(() => {
        console.log('Calculating selected item');
        return items[count % items.length];
    }, [count, items]);

    return (
        <div>
            <h1>Count: {count}</h1>
            <p>Selected Item: {selectedItem}</p>
            <button onClick={() => setCount(count + 1)}>Increment</button>
        </div>
    );
}
