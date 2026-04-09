import React from "react";
import { createContext } from "react";
import { type User } from "./index";

export const userContext = createContext<User | undefined>(undefined);


export const useUserContext = () => {
  const context = React.useContext(userContext);
  if (context === undefined) {
    throw new Error("useUserContext must be used within a UserProvider");
  }
  return context;
}