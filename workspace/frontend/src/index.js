import React from 'react';
import { Route, Link, BrowserRouter as Router } from 'react-router-dom';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import Page_home from "./page_home";
import Page_upload from "./page_upload";
import * as serviceWorker from './serviceWorker';
import Page_notfound from './Page_notfound';
import { Switch } from "react-router-dom";

const routing = (
    <Router>
        <Switch>
                /*<Route exact path="/" component={App} />*/
                <Route exact path="/" component={Page_home} />
                <Route path="/upload" component={Page_upload} />
                <Route path="/home" component={Page_home} />
                <Route component={Page_notfound} />
        </Switch>
    </Router>
);

ReactDOM.render(routing, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
