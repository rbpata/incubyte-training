import React from 'react';
import Child from './child';
import {useState} from 'react';
function Parent() {
    const [count, setCount] = useState(0);

    return (
        <div>
            <h1>Parent Component</h1>
            <p>Count: {count}</p>
            <button onClick={() => setCount(count + 1)}>Increment</button>
            <Child />
        </div>
    );
}

export default Parent;
