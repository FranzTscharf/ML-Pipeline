import React from 'react';
import Header from "./header";
import Footer from "./footer";
import Upload from './upload';

const styleObj2 = {
    paddingBottom: '120px',
    paddingTop: '120px'
};

class Page_notfound extends React.Component {
    render() {
        return (
            <div>
                <Header></Header>
                <div className="uk-container">
                    <div style={styleObj2}>
                        <h1 className="uk-heading-2xlarge uk-margin-small">404</h1>
                        <h1>The page your looking for don't exists</h1>
                        <br></br>
                        <br></br>
                        <br></br>
                        <br></br>
                        <br></br>
                        <br></br>
                        <br></br>
                        <br></br>
                        <br></br>
                        <br></br>
                        <br></br>
                    </div>
                </div>
                <Footer></Footer>
            </div>
        );
    }
}

export default Page_notfound;