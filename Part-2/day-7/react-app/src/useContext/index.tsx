import React, { useState } from 'react'
import Dashboard from './dashboard';
import { userContext } from './context';


export interface User{
  name: string,
}

const Index = () => {
    const user = useState<User>({name: "John Doe"});

  return (

    <div>
      <h1>Use Context example</h1>
    
      <userContext.Provider value={user[0]}>
      <Dashboard />
        </userContext.Provider>
    </div>
  )
}

export default Index
