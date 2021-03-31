import React, { Component } from 'react'
import * as UIkit from "uikit";
import Model_correction from "./model_correction";

const styleObj = {
    display: 'none'
};
const styleObj2 = {
    marginRight: '5px'
};

class Model_display extends React.Component {
    constructor(props) {
        super(props);
        this.element = React.createRef();
        this.element2 = React.createRef();
    }
    componentDidMount() {
        this.element.current.addEventListener('click',function (e) {
            var filename = document.querySelector("#filePath").value;
            var img_path = process.env.REACT_APP_API_GATEWAY_URL + "tmp/" + filename;
            var doc_customer = document.querySelector("#text_customer").value;
            var doc_identification = document.querySelector("#text_identification").value;
            var doc_type = document.querySelector("#text_type").value;
            var doc_content = document.querySelector("#text_content").value;
            var doc_header = document.querySelector("#text_header").value;
            var today = new Date();
            var myHeaders = new Headers();
            myHeaders.append("Content-Type", "application/json");
            var username = "MLAAS_FRONTEND_USER";
            var password = "NotUseMe4AnyThing&Else2";
            var authString = username+':'+password;
            myHeaders.append("Authorization", "Basic "+btoa(authString));
            var raw = JSON.stringify({
                "FILENAME":filename,
                "FILEPATH":img_path,
                "FILEDATE":today,
                "FILECOMMENT":"ok",
                "DOC_CUSTOMER":doc_customer,
                "DOC_IDENTIFICATION":doc_identification,
                "DOC_TYPE":doc_type,
                "DOC_HEADER":doc_header,
                "DOC_CONTENT":doc_content
            });
            var requestOptions = {
                method: 'POST',
                headers: myHeaders,
                body: raw,
                redirect: 'follow'
            };
            fetch(process.env.REACT_APP_API_HANA_DB_ODATA, requestOptions)
                .then(response => response.text())
                .then(result => {
                    console.log(result);
                    var model = document.getElementById("modelDisplay");
                    UIkit.modal(model).hide();
                    window.location.reload();
                }).catch(error => console.log('error', error));

        });
        this.element2.current.addEventListener('click',function (e) {
            var model = document.getElementById("modal-full-split");
            UIkit.modal(model).show();
        })
    }

    render() {
          return (
            <div>
                <div id="modelDisplay" className="uk-modal uk-open">
                    <div className="uk-modal-dialog">
                        <form>
                            <div className="uk-modal-body"><h2 className="uk-modal-title">Dokument-Tagging</h2>
                                <p>Die folgenden systematisch bestimmten Daten werden genutzt um das Dokument dem Vorgang zuzuordnen.</p>
                                <div className="uk-margin"><label className="uk-form-label"
                                                                  htmlFor="form-horizontal-text">Bezeichnung</label>
                                    <div className="uk-form-controls"><input id="input_type" className="uk-input" disabled={true} type="text"
                                                                             placeholder=""/></div>
                                </div>
                                <div className="uk-margin"><label className="uk-form-label"
                                                                  htmlFor="form-horizontal-text">Identifikation</label>
                                    <div className="uk-form-controls"><input id="input_id" className="uk-input" disabled={true} type="text"
                                                                             placeholder=""/></div>
                                </div>
                                <div className="uk-margin"><label className="uk-form-label"
                                                                  htmlFor="form-horizontal-text">Kunde</label>
                                    <div className="uk-form-controls"><input id="input_customer" className="uk-input" disabled={true} type="text"
                                                                             placeholder=""/></div>
                                </div>
                                <div className="uk-margin" style={styleObj}><label className="uk-form-label"
                                                                  htmlFor="form-horizontal-text">Content</label>
                                    <div className="uk-form-controls"><input id="input_content" className="uk-input" disabled={true} type="text"
                                                                             placeholder=""/></div>
                                </div>
                                <div className="uk-margin" style={styleObj}><label className="uk-form-label"
                                                                  htmlFor="form-horizontal-text">Header</label>
                                    <div className="uk-form-controls"><input id="input_header" className="uk-input" disabled={true} type="text"
                                                                             placeholder=""/></div>
                                </div>
                            </div>
                            <div className="uk-modal-footer uk-text-right">
                                <button id="button_edit" className="uk-button uk-button-default uk-modal-close" ref={this.element2} type="button" style={styleObj2}>Bearbeiten</button>
                                <button id="button_okay" className="uk-button uk-button-primary" ref={this.element} type="button">Okay</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

        )
    }
}


export default Model_display;