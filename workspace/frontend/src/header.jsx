import React from 'react';
import Logo from './Mercedes-Benz_Logo_2010.svg'

const styleLogo = {
    width: '171px',
    marginBottom: '9.5px'
};

class Header extends React.Component {
    render() {
        return (
            <div className="App">
                <nav className="uk-navbar-container" id="nav-bar-color" data-uk-sticky>
                    <div className="uk-container">
                        <div uk-navbar="" className="uk-navbar-container uk-navbar-transparent uk-light">
                            <div className="uk-navbar-left">
                                <a className="uk-navbar-item uk-logo" href="./home"><img src={Logo} alt="Logo" style={styleLogo}/></a>
                                <ul className="uk-navbar-nav">
                                    <li className="uk-active"><a href="./home">Home</a></li>
                                    <li><a href="./upload">Upload</a></li>
                                    <li><a href="#">About</a></li>
                                </ul>

                            </div>
                            <div className="uk-navbar-right">
                                <a className="uk-navbar-toggle uk-icon" href="#modal" uk-icon="icon: more-vertical"
                                   uk-toggle="">
                                    <svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"
                                         data-svg="more-vertical">
                                        <circle cx="10" cy="3" r="2"></circle>
                                        <circle cx="10" cy="10" r="2"></circle>
                                        <circle cx="10" cy="17" r="2"></circle>
                                    </svg>
                                </a>
                                <a className="uk-navbar-toggle uk-icon uk-search-icon" href="#modal-search" uk-search-icon=""
                                   uk-toggle="">
                                    <svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"
                                         data-svg="search-icon">
                                        <circle fill="none" stroke="#000" strokeWidth="1.1" cx="9" cy="9" r="7"></circle>
                                        <path fill="none" stroke="#000" strokeWidth="1.1" d="M14,14 L18,18 L14,14 Z"></path>
                                    </svg>
                                </a>
                                <a className="uk-navbar-toggle uk-icon uk-navbar-toggle-icon" href="#offcanvas"
                                   uk-navbar-toggle-icon="" uk-toggle="">
                                    <svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"
                                         data-svg="navbar-toggle-icon">
                                        <rect y="9" width="20" height="2"></rect>
                                        <rect y="3" width="20" height="2"></rect>
                                        <rect y="15" width="20" height="2"></rect>
                                    </svg>
                                </a>
                            </div>
                        </div>
                    </div>
                </nav>
            </div>

        );
    }
}


export default Header;