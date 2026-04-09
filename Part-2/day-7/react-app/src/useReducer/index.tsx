import {useReducer} from 'react';

interface State {
    count: number;
    error: string | null;
}

interface Action {
    type: 'increment' | 'decrement';
}

function reducer(state: State, action: Action) {
    let hasError: boolean;
    switch (action.type) {
        case 'increment':
            hasError = state.count >= 5;
            return {
                count: hasError ? state.count : state.count + 1,
                error: hasError ? 'Count cannot be greater than 5' : null
            };
        case 'decrement':
            hasError = state.count <= 0;
            return {
                count: hasError ? state.count : state.count - 1,
                error: hasError ? 'Count cannot be less than 0' : null
            };
        default:
            return state;
    }
}

export const Index = () => {
    const [state, dispatch] = useReducer(reducer, {count: 0, error: null});

    return (
        <div>
            <h1>Count: {state.count}</h1>
            {state.error && <p style={{color: 'red'}}>{state.error}</p>}
            <button onClick={() => dispatch({type: 'increment'})}>
                Increment
            </button>
            <button onClick={() => dispatch({type: 'decrement'})}>
                Decrement
            </button>
        </div>
    );
};
