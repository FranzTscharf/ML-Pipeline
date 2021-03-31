import React from 'react';

const styleObj1 = {
    'marginTop': '5px',
    'fontSize': '10px'
};
class Footer extends React.Component {
    render() {
        return (
            <div className="uk-section-muted uk-section uk-section-small"
                 uk-scrollspy="target: [uk-scrollspy-class]; cls: uk-animation-slide-left-small; delay: false;">

                <div className="uk-container">
                    <div className="uk-grid-margin uk-grid uk-grid-stack" uk-grid="">
                        <div className="uk-grid-item-match uk-flex-middle uk-width-expand@m uk-first-column">


                            <div className="uk-panel uk-width-1-1">

                                <div
                                    className="uk-margin-remove-vertical uk-text-left@m uk-text-center uk-scrollspy-inview uk-animation-slide-left-small"
                                    uk-scrollspy-class="" >

                                    <a className="el-link" href="http://sap.com"><img width='77px'
                                                                                      className="el-image" alt="Fuse"
                                                                                      data-src="https://upload.wikimedia.org/wikipedia/commons/5/59/SAP_2011_logo.svg" uk-img=""
                                                                                      src="https://upload.wikimedia.org/wikipedia/commons/5/59/SAP_2011_logo.svg"/>
                                    </a>
                                    <p className="uk-text-meta" style={styleObj1}>Made with love by SAP. All rights Reserved.</p>

                                </div>

                            </div>


                        </div>

                        <div className="uk-grid-item-match uk-flex-middle uk-width-1-2@m uk-grid-margin uk-first-column">


                            <div className="uk-panel uk-width-1-1">

                                <div className="uk-text-center uk-scrollspy-inview uk-animation-slide-bottom-small"
                                     uk-scrollspy-class="uk-animation-slide-bottom-small">
                                    <ul className="uk-margin-remove-bottom uk-subnav  uk-subnav-divider uk-flex-center"
                                        uk-margin="">
                                        <li className="el-item uk-first-column">
                                            <a className="el-link"
                                               href="./kontakt">Kontakt</a>
                                        </li>
                                        <li className="el-item">
                                            <a className="el-link"
                                               href="./info">Informationen</a></li>
                                        <li className="el-item">
                                            <a className="el-link"
                                               href="./sponsors">Sponsoren</a></li>
                                    </ul>

                                </div>

                            </div>


                        </div>

                        <div
                            className="uk-grid-item-match uk-flex-middle uk-width-expand@m uk-grid-margin uk-first-column">


                            <div className="uk-panel uk-width-1-1">



                            </div>


                        </div>
                    </div>
                </div>


            </div>

        );
    }
}


export default Footer;