import React from 'react'
import Header from "./header";
import Footer from "./footer";
import Upload from './upload';
import Model_correction from "./model_correction";
import Model_display from "./model_display";

class Page_upload extends React.Component {
    render() {
        return(
            <div name="App">
                <Header></Header>
                <Upload></Upload>
                <Footer></Footer>
            </div>

        )
    }
}
export default Page_upload