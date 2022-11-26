import React from "react";
import { Navigate, Routes, Route, Router } from "react-router-dom";
import RouteGuard from "./components/RouteGuard"

//history
import { history } from './helpers/history';

//pages
import HomePage from "./pages/Home"
import Login from "./pages/Login"

function Routes1() {
    return (
        // <Router history={history}>
            <Routes>
                {/* <Route  path="/"><RouteGuard /></Route> */}
                <Route
                    path="login" element={<Login />}/>
                {/* <Navigate to="/" /> */}
            </Routes>
        // </Router>
    );
}

export default Routes1