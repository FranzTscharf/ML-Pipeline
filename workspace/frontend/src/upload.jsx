import React, { Component } from 'react'
import ReactDOM from 'react-dom';
import * as UIkit from "uikit";
import Model_display from "./model_display";
import Model_correction from "./model_correction";

const styleObjFileElement = {
    'max-width': '250px',
    'white-space': 'nowrap',
    'overflow': 'hidden',
    'text-overflow': 'ellipsis'
};
const styleObjNoContent = {
    'min-height': '300px'
};
const styleObj = {
    padding: '30px'
};
var filename;

class Upload extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            data: [],
        }
    }

    componentDidMount() {
        var myHeaders = new Headers();
        var username = "MLAAS_FRONTEND_USER";
        var password = "NotUseMe4AnyThing&Else2";
        var authString = username+':'+password;
        myHeaders.append("Authorization", "Basic "+btoa(authString));
        var requestOptions = {
                method: 'GET',
                headers: myHeaders,
                redirect: 'follow'
        };
        fetch(process.env.REACT_APP_API_HANA_DB_ODATA+"?$format=json", requestOptions)
                .then(response => response.json())
                .then((result) => this.setState({data: result.d.results}))
                .catch(error => console.log('error', error));

        var bar = document.getElementById('js-progressbar');
        UIkit.upload('.js-upload',{
            url: process.env.REACT_APP_API_GATEWAY_URL + 'gateway/document',
            dataType: 'form-data',
            name: 'file',
            multiple: false,
            allow : '*.(jpg|jpeg|gif|png|pdf)', // allow only pdf and images

            //funcitons executing during upload etc.

            beforeSend: function (environment) {
                console.log('beforeSend', arguments);

                // The environment object can still be modified here.
                // var {data, method, headers, xhr, responseType} = environment;

            },
            beforeAll: function () {
                console.log('beforeAll', arguments);
            },
            load: function () {
                console.log('load', arguments);
            },
            error: function () {
                console.log('error', arguments);
                UIkit.notification({message: 'Upload Failed!', status: 'danger', pos: 'top-right', timeout: 5000});
            },
            complete: function (e) {
                console.log('complete', arguments);
                var upload_response = e.responseText;
                var upload_response_json = JSON.parse(upload_response);
                console.log(upload_response_json.img_name);
                filename = upload_response_json.img_name;
                var pdfname = upload_response_json.pdf_name;
                UIkit.notification({message: 'Upload Completed!', status: 'success', pos: 'top-right', timeout: 3000});
                // eslint-disable-next-line no-undef

                //!#TODO auslagern in function detecttoarray
                fetch(process.env.REACT_APP_API_GATEWAY_URL + "serving/detecttoarray?filename=" + filename)
                    .then(res => res.json())
                    .then(
                        (result) => {
                            console.log(result);
                            bar.value = bar.value + bar.value;
                            UIkit.notification({message: 'Identify tags!', status: 'success', pos: 'top-right', timeout: 2000});
                            //!#TODO auslagern in function roiToText
                            var result_json = JSON.parse(JSON.stringify(result));
                            let formData = new FormData();
                            formData.append('filename', filename);
                            formData.append('json', JSON.stringify(result_json));
                            fetch(process.env.REACT_APP_API_GATEWAY_URL + "ocr/roiToText",{method: 'post',body: formData})
                                .then(res => res.json())
                                .then(
                                    (result) => {
                                        bar.value = bar.value + bar.value;
                                        console.log(result);
                                        //!#TODO into extra function
                                        //Set the D3 Data array with the putput of the gateway tf.serving instances
                                        //that means the positions of the bounding boxes in D3.js

                                        //!#TODO into extra function
                                        //pass the koordinates of the tf.serving to the d3 model correktion Dialog window etc. popup for the bounding boxes
                                        ReactDOM.render(React.createElement(Model_correction,{inputData: result_json}), document.getElementById("ID_Model_correction"));

                                        //!#TODO if not (('identification' || 'customer') and 'type') exists in result => direct zur manuellen verarbeitung
                                        var result_rep = result.replace(/'/g,'"');
                                        var jsonObj = JSON.parse(result_rep);
                                        if (typeof jsonObj['type'] != 'undefined'){
                                            var doc_type = jsonObj['type'];
                                        } else {var doc_type = ""}
                                        if (typeof jsonObj['identification'] != 'undefined'){
                                            var doc_identification = jsonObj['identification'];
                                        } else {var doc_identification = ""}
                                        if (typeof jsonObj['customer'] != 'undefined'){
                                            var doc_customer = jsonObj['customer'];
                                        } else {var doc_customer = ""}
                                        if (typeof jsonObj['header'] != 'undefined'){
                                            var doc_header = jsonObj['header'];
                                        } else {var doc_header = ""}
                                        if (typeof jsonObj['content'] != 'undefined'){
                                            var doc_content = jsonObj['content'];
                                        } else {var doc_content = ""}
                                        if ((typeof doc_identification != 'undefined') && (doc_identification.toLowerCase().match("auftr*agsnu*"))) {
                                            var start = doc_identification.toLowerCase().search("auftr*agsnu*");
                                            //split from start to end and take the resulting string
                                            // console.log(auftragsnummer);
                                            var auftragsnummer = doc_identification.slice(start, start+35);
                                            console.log(start);
                                            console.log(auftragsnummer);
                                            //only keep numbers
                                            doc_identification = auftragsnummer.replace(/\D/g,'');
                                            console.log(doc_identification);
                                        }
                                        console.log(jsonObj);

                                        //#!TODO auslagern in externe Funktion um Werte zu schreiben.
                                        var model = document.getElementById("modelDisplay");
                                        // Set the input fields
                                        document.getElementById("input_type").placeholder = doc_type;
                                        document.getElementById("input_id").placeholder = doc_identification;
                                        document.getElementById("input_customer").placeholder = doc_customer;
                                        document.getElementById("input_content").placeholder = doc_content;
                                        document.getElementById("input_header").placeholder = doc_header;

                                        document.getElementById("text_type").value = doc_type;
                                        document.getElementById("text_identification").value = doc_identification;
                                        document.getElementById("text_customer").value = doc_customer;
                                        document.getElementById("text_header").value = doc_header;
                                        document.getElementById("text_content").value = doc_content;
                                        document.getElementById("imgId").value = filename;
                                        if(typeof pdfname != 'undefined'){
                                            document.querySelector("#filePath").value = pdfname;
                                        } else {
                                            document.querySelector("#filePath").value = filename;
                                        }
                                        //set the image src etc. url
                                        document.querySelector("#documentPicture").src = process.env.REACT_APP_API_GATEWAY_URL + "tmp/" + filename;
                                        UIkit.modal(model).show();
                                        UIkit.notification({message: 'All Done!', status: 'success', pos: 'top-right', timeout: 3000});
                                        bar.value = 0;
                                    },
                                    // Note: it's important to handle errors here
                                    // instead of a catch() block so that we don't swallow
                                    // exceptions from actual bugs in components.
                                    (error) => {
                                        UIkit.notification({message: 'File detection failed!', status: 'danger', pos: 'top-right', timeout: 5000});
                                        console.error(error);
                                    }
                                )


                        },
                        // Note: it's important to handle errors here
                        // instead of a catch() block so that we don't swallow
                        // exceptions from actual bugs in components.
                        (error) => {
                            console.error(error);
                            UIkit.notification({message: 'File detection failed!', status: 'danger', pos: 'top-right', timeout: 5000});
                        }
                    )


            },

            loadStart: function (e) {
                console.log('loadStart', arguments);
                bar.removeAttribute('hidden');
                bar.max = e.total;
                bar.value = e.loaded;
            },

            progress: function (e) {
                console.log('progress', arguments);

                bar.max = e.total;
                bar.value = e.loaded / 3;
            },

            loadEnd: function (e) {
                console.log('loadEnd', arguments);

                bar.max = e.total;
                bar.value = e.loaded / 3;
            },

            completeAll: function (e) {
                var upload_response = e.responseText;
                console.log('completeAll', arguments);

                //setTimeout(function () {
                //    bar.setAttribute('hidden', 'hidden');
                //}, 1000);
            }

        });
    }
    renderTable(){
        return (this.state.data.sort((a, b) => new Date(a.FILEDATE) - new Date(b.FILEDATE)).reverse().map((doc, index) => (
                <tr>
                    <td><code>{doc.FILENAME}</code></td>
                    <td>{doc.FILEDATE}</td>
                    <td><a class="uk-link-text" href={doc.FILEPATH}>{doc.FILEPATH.split('.').pop().toUpperCase()}</a></td>
                    <td>
                        {doc.DOC_IDENTIFICATION.length > 0 && <span className="uk-label" style={styleObjFileElement}>{doc.DOC_IDENTIFICATION}</span>} {doc.DOC_TYPE.length > 0 && <span className="uk-label" style={styleObjFileElement}>{doc.DOC_TYPE}</span>} {doc.DOC_CUSTOMER.length > 0 && <span className="uk-label" style={styleObjFileElement}>{doc.DOC_CUSTOMER}</span>} {doc.DOC_CONTENT.length > 0 && <span className="uk-label" style={styleObjFileElement}>{doc.DOC_CONTENT}</span>} {doc.DOC_HEADER.length > 0 && <span className="uk-label" style={styleObjFileElement}>{doc.DOC_HEADER}</span>}
                    </td>
                </tr>
            )));
    }

    render() {

        return (

            <div className="uk-container" style={styleObj}>

                <h1>Upload</h1>

                <h2>Datei auswählen</h2>

                <div className="js-upload uk-placeholder uk-text-center">
                    <span uk-icon="icon: cloud-upload" className="uk-icon"><svg width="20" height="20"
                                                                                viewBox="0 0 20 20"
                                                                                xmlns="http://www.w3.org/2000/svg"
                                                                                data-svg="cloud-upload"><path
                        fill="none" stroke="#000" strokeWidth="1.1"
                        d="M6.5,14.61 L3.75,14.61 C1.96,14.61 0.5,13.17 0.5,11.39 C0.5,9.76 1.72,8.41 3.31,8.2 C3.38,5.31 5.75,3 8.68,3 C11.19,3 13.31,4.71 13.89,7.02 C14.39,6.8 14.93,6.68 15.5,6.68 C17.71,6.68 19.5,8.45 19.5,10.64 C19.5,12.83 17.71,14.6 15.5,14.6 L12.5,14.6"></path><polyline
                        fill="none" stroke="#000" points="7.25 11.75 9.5 9.5 11.75 11.75"></polyline><path fill="none"
                                                                                                           stroke="#000"
                                                                                                           d="M9.5,18 L9.5,9.5"></path></svg></span>
                    <span className="uk-text-middle"> Ziehen Sie Dateien per Drag & Drop hinein oder </span>
                    <div uk-form-custom="" className="uk-form-custom">
                        <input type="file" multiple=""></input>
                            <span className="uk-link">wählen Sie eine Datei aus.</span>
                    </div>
                </div>

                <progress id="js-progressbar" className="uk-progress" value="0" max="100" hidden></progress>

                <h2>Liste der verarbeiteten Dokumente</h2>
                <div className="uk-overflow-auto" style={styleObjNoContent}>
                    <table className="uk-table uk-table-striped uk-table-hover">
                        <thead>
                        <tr>
                            <th>Name</th>
                            <th>Datum</th>
                            <th>Download</th>
                            <th>Tags</th>
                        </tr>
                        </thead>
                        <tbody>
                        {this.renderTable()}
                        </tbody>
                    </table>

                </div>
            <Model_display childRef={this.myRef}/>
            <div id="ID_Model_correction"></div>
        </div>
        )
    }


}


export default Upload;