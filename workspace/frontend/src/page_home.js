import React from 'react'
import './App.css';
import Header from './header.jsx';
import Home from './home.jsx';
import Slider from './slider.jsx';
import Footer from './footer.jsx';

class Page_home extends React.Component {
    render() {
        return(
            <div name="App">
                <Header></Header>

                <Home></Home>
                <Footer></Footer>

            </div>
        )
    }
}
export default Page_home