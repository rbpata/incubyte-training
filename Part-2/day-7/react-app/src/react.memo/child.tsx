import React from 'react';

function Child() {
    console.log('Child component rendered');
    return <div>Child</div>;
}

export default React.memo(Child);
