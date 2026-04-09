import React, {type JSX} from 'react';
import {lazy} from 'react';
// import { SideBar } from './component';
const Profile = lazy(() =>
    import('./component').then((module) => ({default: module.Profile}))
);
const SideBar = lazy(() =>
    import('./component').then((module) => ({default: module.SideBar}))
);

function Dashboard(): JSX.Element {
    return (
        <div>
            <h1>Dashboard</h1>
            <SideBar />
            <Profile />
        </div>
    );
}

export default Dashboard;
