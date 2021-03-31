import React from 'react';
import Slider from './slider.jsx';

const styleObj2 = {
    'text-align': 'left',
    'margin-left': '10px'
};

class Home extends React.Component {
    render() {
        return (
            <div className="uk-section-default uk-section uk-flex uk-flex-middle"
                 uk-scrollspy="target: [uk-scrollspy-class]; cls: uk-animation-slide-left-medium; delay: false;"
                 uk-height-viewport="offset-top: true; offset-bottom: true;" id="content-margen">
            <div className="uk-width-1-1">

                <div className="uk-container">
                    <div className="uk-grid-large uk-grid-margin-large uk-grid" uk-grid="">
                        <div className="uk-grid-item-match uk-flex-middle uk-width-expand@m uk-first-column">


                            <div className="uk-panel uk-width-1-1">

                                <h1 className="uk-h6 uk-text-left@m uk-text-center uk-scrollspy-inview uk-animation-slide-left-medium"
                                    uk-scrollspy-class=""> Warum noch ein System? </h1>
                                <h2 className="uk-h1 uk-width-xlarge uk-margin-auto uk-text-left@m uk-text-center uk-scrollspy-inview uk-animation-slide-left-medium"
                                    uk-scrollspy-class=""> Der neue Weg, um Dokumente zu sortieren.
                                    </h2>
                                <div
                                    className="uk-margin uk-text-left@m uk-text-center uk-scrollspy-inview uk-animation-slide-left-medium"
                                    uk-scrollspy-class="">Mit Hilfe von künstlicher Intelligenz in Form von Deep Learning können
                                    Dokumente schnell und zuverlässig sortiert und klassifiziert werden.</div>
                                <div
                                    className="uk-margin-large uk-text-left@m uk-text-center uk-scrollspy-inview uk-animation-slide-left-medium"
                                    uk-scrollspy-class="">


                                    <a className="el-content uk-button uk-button-default" title="Explore"
                                       href="./upload">
                                        Entdecken
                                    </a>


                                </div>

                            </div>


                        </div>

                        <div className="uk-grid-item-match uk-flex-middle uk-width-expand@m">


                            <div className="uk-panel uk-width-1-1">

                                <div className="uk-margin uk-text-center uk-scrollspy-inview uk-animation-slide-right"
                                     uk-scrollspy-class="uk-animation-slide-right">
                                    <div className="uk-flex">

                                        <div className="uk-flex-last" style={styleObj2}>

                                            <ul className="uk-list">
                                                <li className="uk-text-meta">Erkennung:</li>
                                                <li><span className="uk-label uk-label-success">Bestellung</span></li>
                                                <li><span className="uk-label uk-label-success">0 9 523 07587</span></li>
                                                <li><span className="uk-label uk-label-success">Kristina Rausch</span></li>
                                            </ul>

                                        </div>
                                        <div className="">
                                            <Slider></Slider>
                                        </div>
                                    </div>
                                </div>

                            </div>


                        </div>
                    </div>
                </div>
            </div>
            </div>

        );
    }
}

export default Home;