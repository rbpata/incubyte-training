import React from "react";
import { useUserContext } from "./context";

export const SideBar = () => {
  const user = useUserContext();
  return (
    <div>
      <h1>SideBar</h1>
      <h2>{user.name}</h2>
    </div>
  );
};


export const Profile = () => {
  const user = useUserContext();
  return (
    <div>
      <h1>Profile</h1>
      <h2>{user.name}</h2>
    </div>
  );
}