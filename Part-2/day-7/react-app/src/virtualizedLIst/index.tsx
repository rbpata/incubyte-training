import React, {useState} from 'react';

const Index = () => {
    const [items, setItems] = useState(
        Array.from({length: 1000}, (_, index) => `Item ${index + 1}`)
    );
    const [scrollTop, setScrollTop] = useState(0);

    // Configuration
    const ITEM_HEIGHT = 30; // Height of each list item
    const CONTAINER_HEIGHT = 400;
    const BUFFER_SIZE = 5; // Extra items to render above and below viewport

    // Calculate visible range
    const startIndex = Math.max(
        0,
        Math.floor(scrollTop / ITEM_HEIGHT) - BUFFER_SIZE
    );
    const endIndex = Math.min(
        items.length,
        Math.ceil((scrollTop + CONTAINER_HEIGHT) / ITEM_HEIGHT) + BUFFER_SIZE
    );

    // Get only visible items
    const visibleItems = items.slice(startIndex, endIndex);

    // Calculate spacer heights to maintain scroll position
    const topSpacerHeight = startIndex * ITEM_HEIGHT;
    const bottomSpacerHeight = (items.length - endIndex) * ITEM_HEIGHT;

    return (
        <div>
            <h1>Virtualized List example</h1>
            <p>
                Total items: {items.length} | Rendering: {visibleItems.length}
            </p>
            <div
                style={{height: `${CONTAINER_HEIGHT}px`, overflow: 'auto'}}
                onScroll={(e) => {
                    const target = e.target as HTMLDivElement;
                    const newScrollTop = target.scrollTop;
                    setScrollTop(newScrollTop);

                    const clientHeight = target.clientHeight;
                    const scrollHeight = target.scrollHeight;

                    // Load more items when scrolled near the bottom
                    if (newScrollTop + clientHeight >= scrollHeight - 100) {
                        setItems((prevItems) => [
                            ...prevItems,
                            ...Array.from(
                                {length: 1000},
                                (_, index) =>
                                    `Item ${prevItems.length + index + 1}`
                            )
                        ]);
                    }
                }}
            >
                <ul style={{margin: 0, padding: 0, listStyle: 'none'}}>
                    {/* Top spacer */}
                    {topSpacerHeight > 0 && (
                        <div style={{height: `${topSpacerHeight}px`}} />
                    )}

                    {/* Visible items */}
                    {visibleItems.map((item, index) => (
                        <li
                            key={startIndex + index}
                            style={{
                                height: `${ITEM_HEIGHT}px`,
                                padding: '5px 10px',
                                borderBottom: '1px solid #eee'
                            }}
                        >
                            {item}
                        </li>
                    ))}

                    {/* Bottom spacer */}
                    {bottomSpacerHeight > 0 && (
                        <div style={{height: `${bottomSpacerHeight}px`}} />
                    )}
                </ul>
            </div>
        </div>
    );
};

export default Index;
