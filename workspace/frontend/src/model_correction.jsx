import React, { Component } from 'react'
import * as d3 from "d3";
import * as UIkit from "uikit";
import Tesseract from 'tesseract.js';
import { createWorker } from 'tesseract.js';
import ExampleDocument from './example_document.jpg';
import { encode } from "base-64";


const styleObj = {
    minHeight: 'calc(100vh)',
    maxWidth: 'fit-content',
    borderRight: '1.5px solid',
    borderRightColor: '#b5b5b594'
};

const styleObj2 = {
    backgroundColor: '#f0506e',
    width: '100%'
};
const styleObj3 = {
    float: 'right'
};
const styleObj4 = {
    marginRight: '5px'
};

const styleObjSpinner = {
    height: '20px',
    width: '20px',
    color: '#1e86f0'
};
const styleObjInLine = {
    display: 'block'
};
const styleObjSpinnerDiv = {
    display: 'none'
};
class Model_correction extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data: props.inputData,
        };
    }
    componentDidMount() {
        var init = 0;
        var convData = this.state.data;
        var data = [
            /*
            {id: 1, x: 100, y: 200, width: 149, height: 50, label: "Identification"},
            {id: 2, x: 100, y: 300, width: 149, height: 50, label: "Customer"},
            {id: 3, x: 100, y: 400, width: 149, height: 50, label: "Type"}
            */
        ];
        var MAP_HEIGHT = 2500;
        var MAP_WIDTH = MAP_HEIGHT * Math.sqrt(2);

        var MAX_TRANSLATE_X = MAP_WIDTH / 2;
        var MIN_TRANSLATE_X = -MAX_TRANSLATE_X;

        var MAX_TRANSLATE_Y = MAP_HEIGHT / 2;
        var MIN_TRANSLATE_Y = -MAX_TRANSLATE_Y;

        var MIN_RECT_WIDTH = 5;
        var MIN_RECT_HEIGHT = 5;

        var HANDLE_R = 5;
        var HANDLE_R_ACTIVE = 12;

        var wrapper = document.getElementById("svgWrapper");

        var height = wrapper.offsetHeight;
        var width = wrapper.offsetWidth;

        /*
        var
            inpX = document.getElementById("x"),
            inpY = document.getElementById("y"),
            inpWidth = document.getElementById("width"),
            inpHeight = document.getElementById("height");
        */
        var svg = d3.select("#svgID");

        // for the background
        svg.append("rect")
            .style("fill", "transparent")
            .attr("width", "100%")
            .attr("height", "100%");

        var g = svg.append("g");

        // if model is showing reload the position of the bounding boxes
        var model = document.getElementById("modal-full-split");
        UIkit.util.on('#modal-full-split', 'show', function () {
            checkElement("#svgID").then((element) => {
                if (init == 0) {
                    fillData(element);
                    init = 1;
                }
            });
        });
        async function checkElement(selector) {
            const querySelector = document.querySelector(selector);
            while ((querySelector < 1) && (typeof querySelector !== 'undefined')) {
                await rafAsync()
            }
            return querySelector;
        }
        function rafAsync() {
            return new Promise(resolve => {
                requestAnimationFrame(resolve); //faster than set time out
            });
        }
        function fillData(element = document.querySelector("#svgID")) {
            if ((typeof convData !== 'undefined') || (convData !== '')) {
                var drawObj = element;  //document.querySelector("#svgID");
                var img = document.querySelector("#documentPicture");
                var box_id = 0;
                var newData = [];
                convData.forEach(function (x) {
                    var box_score = x[1];
                    var box_class = x[0];
                    var box_x = (x[2] * drawObj.width.animVal.value) / img.naturalWidth;
                    var box_y = (x[3] * drawObj.height.animVal.value) / img.naturalHeight;
                    var box_width = ((x[4] - x[2]) * drawObj.width.animVal.value) / img.naturalWidth;
                    var box_height = ((x[5] - x[3]) * drawObj.height.animVal.value) / img.naturalHeight;
                    newData.push({id: box_id, x: box_x, y: box_y, width: box_width, height: box_height, label: box_class, score: box_score});
                    box_id = box_id + 1;
                });
                data = newData;
                update();
            }
        }
        function resizerHover() {
            var el = d3.select(this), isEntering = d3.event.type === "mouseenter";
            el
                .classed("hovering", isEntering)
                .attr(
                    "r",
                    isEntering || el.classed("resizing") ?
                        HANDLE_R_ACTIVE : HANDLE_R
                );
        }

        function rectResizeStartEnd() {
            var el = d3.select(this), isStarting = d3.event.type === "start";
            d3.select(this)
                .classed("resizing", isStarting)
                .attr(
                    "r",
                    isStarting || el.classed("hovering") ?
                        HANDLE_R_ACTIVE : HANDLE_R
                );
        }

        function rectResizing(d) {

            //document.querySelector("#deleteIcon").setAttribute("cx",d.width)
            var dragX = Math.max(
                Math.min(d3.event.x, MAX_TRANSLATE_X),
                MIN_TRANSLATE_X
            );

            var dragY = Math.max(
                Math.min(d3.event.y, MAX_TRANSLATE_Y),
                MIN_TRANSLATE_Y
            );

            if (d3.select(this).classed("topleft")) {

                var newWidth = Math.max(d.width + d.x - dragX, MIN_RECT_WIDTH);

                d.x += d.width - newWidth;
                d.width = newWidth;

                var newHeight = Math.max(d.height + d.y - dragY, MIN_RECT_HEIGHT);

                d.y += d.height - newHeight;
                d.height = newHeight;

            } else {

                d.width = Math.max(dragX - d.x, MIN_RECT_WIDTH);
                d.height = Math.max(dragY - d.y, MIN_RECT_HEIGHT);

            }

            update();
        }

        function rectMoveStartEnd(d) {
            d3.select(this).classed("moving", d3.event.type === "start");
        }
        function detectContent(d){
            console.log(d);
            var drawObj = document.querySelector("#svgID");
            var img = document.getElementById("documentPicture");
            var canvas = document.createElement("CANVAS");
            var img_x = (d.x / drawObj.width.animVal.value) * img.naturalWidth;
            var img_y = (d.y / drawObj.height.animVal.value) * img.naturalHeight;
            var img_width = (d.width / drawObj.width.animVal.value) * img.naturalWidth;
            var img_height = (d.height / drawObj.height.animVal.value) * img.naturalHeight;
            console.log(img_x, img_y, img_width, img_height);
            //canvas.setAttribute("width","300");
            //canvas.setAttribute("height","500");
            canvas.setAttribute("width",img_width);
            canvas.setAttribute("height",img_height);
            //document.body.appendChild(canvas);
            //var canvas = document.getElementById('myCanvas');
            var context = canvas.getContext('2d');
            var imageObj = new Image();
            imageObj.crossOrigin = "Anonymous";
            imageObj.src = img.src;
            imageObj.onload = function() {
                // draw cropped image
                var sourceX = img_x;//d.x; //x from element
                var sourceY = img_y;//d.y; //y from element
                var sourceWidth = img_width;//d.width; //Width from element
                var sourceHeight = img_height;//d.height; //Height from element
                var destWidth = sourceWidth;
                var destHeight = sourceHeight;
                var destX = 0;
                var destY = 0;
                context.drawImage(imageObj, sourceX, sourceY, sourceWidth, sourceHeight, destX, destY, destWidth, destHeight);
                Tesseract.recognize(canvas).progress((p) => {
                    //console.log(p.progress);
                    try {
                        //show the spinner in the responsible text field
                        document.querySelector("#spinner_" + d.label).style.display = '';
                    } catch(err) {
                        console.log(err);
                    }
                }).then((r) => {
                    //console.log(r.text);
                    try{
                        document.querySelector("#spinner_" + d.label).style.display = 'none';
                        document.querySelector("#text_" + d.label).value = r.text;
                    } catch(err){
                        console.log(err);
                    }
                })
            };
        }

        function rectMoving(d) {

            var dragX = Math.max(
                Math.min(d3.event.x, MAX_TRANSLATE_X - d.width),
                MIN_TRANSLATE_X
            );

            var dragY = Math.max(
                Math.min(d3.event.y, MAX_TRANSLATE_Y - d.height),
                MIN_TRANSLATE_Y
            );

            d.x = dragX;
            d.y = dragY;
            //detectContent(d);
            update();
        }
        function getAllData(){
            var g = d3.select("#svgID");
            var data = g.selectAll("g.rectangle").data();
            return data;
        }

        function addRect(newRects){

            newRects.append("rect")
                .classed("bg", true)
                .attr("fill", "transparent")
                .attr("stroke", "#f0506e")
                .attr("stroke-width", 1)
                .call(d3.drag()
                    .container(g.node())
                    .on("start end", rectMoveStartEnd)
                    .on("drag", rectMoving)
                    .on("end", detectContent)
                );

            newRects.append("g").classed("circles", true).each(function (d) {
                var circleG = d3.select(this);
                var editCircle = circleG.append("circle")
                    .classed("topright", true)
                    .attr("id", "deleteIcon")
                    .attr("cx", d.width)
                    .attr("cy", 0)
                    .attr("r", HANDLE_R)
                    .on("mouseenter", function(f){
                        d3.select(this).style('fill', '#f0506e');
                        d3.select(this.parentNode).select("svg").selectAll("path").each(function(e,i) {
                            d3.select(this).attr("stroke","white");
                        });
                    })
                    .on("mouseleave", function(f){
                        d3.select(this).style('fill', '#fff');
                        d3.select(this.parentNode).select("svg").selectAll("path").each(function(e,i) {
                            d3.select(this).attr("stroke","#f0506e");
                        });
                    })
                    .on("click", function(f) {
                        d3.select(this.parentNode.parentNode).remove();
                        data = d3.select("#svgID").selectAll("g.rectangle").data();
                        console.log(data);
                        document.getElementById("text_" + d.label).value = "";
                        //alert("on click" + d.className);
                    });

                circleG.append("circle")
                    .classed("topleft", true)
                    .style('fill', "grey")
                    .style('fill-opacity', '0.1')
                    .style('cursor', 'move')
                    .style('stroke-dasharray','5')
                    .style('stroke', 'grey')
                    .style('r', 10)
                    .attr("r", HANDLE_R)
                    .on("mouseenter mouseleave", resizerHover)
                    .on("mouseup", detectContent)
                    .call(d3.drag()
                        .container(g.node())
                        .subject(function () {
                            return {x: d3.event.x, y: d3.event.y};
                        })
                        .on("start end", rectResizeStartEnd)
                        .on("drag", rectResizing)
                    );

                circleG
                    .append("circle")
                    .classed("bottomright", true)
                    .style('fill', "grey")
                    .style('fill-opacity', '0.1')
                    .style('cursor', 'move')
                    .style('stroke-dasharray','5')
                    .style('stroke', 'grey')
                    .style('r', 10)
                    .attr("r", HANDLE_R)
                    .on("mouseenter mouseleave", resizerHover)
                    .call(d3.drag()
                        .container(g.node())
                        .subject(function () {
                            return {x: d3.event.x, y: d3.event.y};
                        })
                        .on("start end", rectResizeStartEnd)
                        .on("end", detectContent)
                        .on("drag", rectResizing)
                    );
                circleG
                    .append("text")
                    .attr("class", "labelText")
                    .attr("dx", 12)
                    .attr("dy", -2)
                    .attr("font-size", "10px")
                    .text(d.label);
                var editIcon = circleG.append("svg").attr("x", d.width).attr("y", -8).classed("toprightsvg", true);
                editIcon.append("path").attr("stroke", "#f0506e").attr("stroke-width","1.06").attr("d","M16,16 L4,4").attr("transform", "scale(0.8)");
                editIcon.append("path").attr("stroke", "#f0506e").attr("stroke-width","1.06").attr("d","M16,4 L4,16").attr("transform", "scale(0.8)");
            });
        }

        function onClickAdd(labelText){
            console.log(labelText);
            document.querySelector("#dropdownClasses").classList.remove("uk-open");
            data.push({id: 12, x: 100, y: 200, width: 150, height: 150, label: labelText});
            update();
        }
        function update() {
            var rects = g.selectAll("g.rectangle").data(data, function (d) {
                return d;
            });

            rects.exit().remove();

            var newRects = rects.enter().append("g").classed("rectangle", true);
            addRect(newRects);


            var allRects = newRects.merge(rects);

            allRects
                .attr("transform", function (d) {
                    return "translate(" + d.x + "," + d.y + ")";
                });

            allRects
                .select("rect.bg")
                .attr("height", function (d) {
                    return d.height;
                })
                .attr("width", function (d) {
                    return d.width;
                });


            allRects
                .select("circle.bottomright")
                .attr("cx", function (d) {
                    return d.width;
                })
                .attr("cy", function (d) {
                    return d.height;
                });
            allRects
                .select("circle.topright")
                .attr("cx", function (d) {
                    return d.width;
                });
            allRects
                .select("svg.toprightsvg")
                .attr("x", function (d) {
                    return d.width -8.1;
                });

            /*
            inpX.value = data[0].x;
            inpY.value = data[0].y;
            inpWidth.value = data[0].width;
            inpHeight.value = data[0].height;
            */
            //write data to current array of rectangels
            //console.log(data);
        }

        function controlChange() {
            data[0][this.id] = +this.value;
            update();
        }
        function initElements(){
            //draw elements
            update();
            //enable dropdown and hide it of the add menue bar item
            UIkit.dropdown(document.querySelector("#dropdownClasses")).hide();
            //add listeners to add new bpunding boxes
            document.querySelectorAll('[id^="add"]').forEach(function (e) {
                e.addEventListener("click", function (d) {
                    onClickAdd(e.innerText);
                });
            });
            document.getElementById("button_reset").addEventListener("click",function (e) {
                fillData();
                document.getElementById("text_type").value = document.getElementById("input_type").placeholder;
                document.getElementById("text_identification").value = document.getElementById("input_id").placeholder;
                document.getElementById("text_customer").value = document.getElementById("input_customer").placeholder;
                document.getElementById("text_header").value = document.getElementById("input_header").placeholder;
                document.getElementById("text_content").value = document.getElementById("input_content").placeholder;
            });

        }

        initElements();

    }

    render() {
          return (
            <div>
                <div id="modal-full-split" className="uk-modal-full uk-modal" uk-modal="">
                    <button className="uk-modal-close-full uk-icon uk-close" type="button" uk-close="">
                        <svg width="14" height="14" viewBox="0 0 14 14" xmlns="http://www.w3.org/2000/svg"
                             data-svg="close-icon">
                            <line fill="none" stroke="#000" strokeWidth="1.1" x1="1" y1="1" x2="13" y2="13"></line>
                            <line fill="none" stroke="#000" strokeWidth="1.1" x1="13" y1="1" x2="1" y2="13"></line>
                        </svg>
                    </button>
                    <div className="uk-modal-dialog">
                        <div className="uk-grid-collapse uk-child-width-1-2@s uk-flex-middle uk-grid" uk-grid="">
                            <div className="uk-background-cover uk-first-column"
                                 style={styleObj}
                                 uk-height-viewport="">
                                <div className="uk-button-group" style={styleObj2}>
                                    <button className="uk-button uk-button-danger" id="button_reset">Reset</button>
                                    <div className="uk-inline">
                                        <button className="uk-button uk-button-danger" type="button" aria-expanded="false">Add</button>
                                        <div className="uk-dropdown" id="dropdownClasses">
                                            <ul className="uk-nav uk-dropdown-nav">
                                                <li className="uk-nav-header">Classes</li>
                                                <li className="uk-nav-divider"></li>
                                                    <li id="add_id"><a>identification</a></li>
                                                    <li id="add_type"><a>type</a></li>
                                                    <li id="add_customer"><a>customer</a></li>
                                                    <li id="add_content"><a>content</a></li>
                                                    <li id="add_header"><a>header</a></li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                                <div className="uk-vertical-align-middle">
                                    <div className="img-overlay-wrap">
                                        <img id="documentPicture"
                                               src={ExampleDocument}></img>
                                        <input type="hidden" id="imgId"></input>
                                        <input type="hidden" id="filePath"></input>
                                        <div id="svgWrapper">
                                            <svg id="svgID"></svg>
                                        </div>
                                    </div>
                                </div>
                                <fieldset id="controls" hidden={true}>
                                    <label>x:<input type="text" id="x"/></label>
                                    <label>y:<input type="text" id="y"/></label>
                                    <label>width:<input type="text" id="width"/></label>
                                    <label>height:<input type="text" id="height"/></label>
                                </fieldset>


                            </div>
                            <div className="uk-padding-large">
                                <h1>Dokument-Tagging</h1>
                                <p>Verschieben Sie die Rechtecke über die Bereiche des Dokuments, die für das Tagging genutzt werden sollen. Die Abschnitte können gelöscht oder neu hinzugefügt werden.</p>
                                <form className="uk-form-stacked">

                                    <div className="uk-margin">
                                        <label className="uk-form-label" htmlFor="text_Identification">Identifikation:</label>
                                        <div className="uk-form-controls">
                                            <div className="uk-inline" style={styleObjInLine}>
                                                <div className="uk-form-icon uk-form-icon-flip uk-icon" id="spinner_identification" style={styleObjSpinnerDiv}>
                                                     <span className="uk-margin-small-right uk-icon uk-spinner" uk-spinner="ratio: 3" style={styleObjSpinner}></span>
                                                </div>
                                                <input className="uk-input" id="text_identification" type="text"
                                                       placeholder="Auftragsnummer, FIN, ..."/>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="uk-margin">
                                        <label className="uk-form-label" htmlFor="text_Type">Type:</label>
                                        <div className="uk-form-controls">
                                            <div className="uk-inline" style={styleObjInLine}>
                                                <div className="uk-form-icon uk-form-icon-flip uk-icon" id="spinner_type" style={styleObjSpinnerDiv}>
                                                    <span className="uk-margin-small-right uk-icon uk-spinner" uk-spinner="ratio: 3" style={styleObjSpinner}></span>
                                                </div>
                                                <input className="uk-input" id="text_type" type="text"
                                                       placeholder="Bestellung PKW, Zahlungsübersicht, ..."/>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="uk-margin">
                                        <label className="uk-form-label" htmlFor="text_Customer">Customer:</label>
                                        <div className="uk-form-controls">
                                            <div className="uk-inline" style={styleObjInLine}>
                                                <div className="uk-form-icon uk-form-icon-flip uk-icon" id="spinner_customer" style={styleObjSpinnerDiv}>
                                                    <span className="uk-margin-small-right uk-icon uk-spinner" uk-spinner="ratio: 3" style={styleObjSpinner}></span>
                                                </div>
                                                <textarea className="uk-textarea" id="text_customer"
                                                          rows="2" placeholder="Herr. Max Mustermann
                                                          Dorfstr. 11
                                                          10119 Berlin
                                                          "></textarea>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="uk-margin">
                                        <label className="uk-form-label" htmlFor="form-h-textarea-content">Content:</label>
                                        <div className="uk-form-controls">
                                            <div className="uk-inline" style={styleObjInLine}>
                                                <div className="uk-form-icon uk-form-icon-flip uk-icon" id="spinner_content" style={styleObjSpinnerDiv}>
                                                    <span className="uk-margin-small-right uk-icon uk-spinner" uk-spinner="ratio: 3" style={styleObjSpinner}></span>
                                                </div>
                                                <textarea className="uk-textarea" id="text_content"
                                                          rows="2" placeholder="Ihre Bestellung über einen PKW ist eingeganen und ..."></textarea>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="uk-margin" style={styleObjSpinnerDiv}>
                                        <label className="uk-form-label" htmlFor="form-h-textarea-content">Header:</label>
                                        <div className="uk-form-controls">
                                            <div className="uk-inline" style={styleObjInLine}>
                                                <div className="uk-form-icon uk-form-icon-flip uk-icon" id="spinner_header" style={styleObjSpinnerDiv}>
                                                    <span className="uk-margin-small-right uk-icon uk-spinner" uk-spinner="ratio: 3" style={styleObjSpinner}></span>
                                                </div>
                                                <textarea className="uk-textarea" id="text_header"
                                                          rows="2" placeholder=""></textarea>
                                            </div>
                                        </div>
                                    </div>
                                    <p className="uk-margin uk-position-relative uk-position-right" style={styleObj3}>
                                        <button className="uk-button uk-button-default" style={styleObj4} id="button_cancel">Abbrechen</button>
                                        <button className="uk-button uk-button-primary" id="button_okay" onClick={handleFeedback}>Okay</button>
                                    </p>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        );
        function handleFeedback(e) {
            e.preventDefault();
            var drawObj = document.querySelector("#svgID");
            var img = document.querySelector("#documentPicture");
            var filename = document.querySelector("#imgId").value;
            var dataParse = d3.select("#svgID").selectAll("g.rectangle").data();
            dataParse.forEach(function(d){
                d.imgWidth = img.naturalWidth;
                d.imgHeight = img.naturalHeight;
                d.filename = filename;
                d.xmin = (d.x / drawObj.width.animVal.value) * img.naturalWidth;
                d.ymin = (d.y / drawObj.height.animVal.value) * img.naturalHeight;
                d.xmax = d.xmin + ((d.width / drawObj.width.animVal.value) * img.naturalWidth);
                d.ymax = d.ymin + ((d.height / drawObj.height.animVal.value) * img.naturalHeight);
            });
            console.log(dataParse);
            let formData = new FormData();
            formData.append('json', JSON.stringify(dataParse));
            fetch(process.env.REACT_APP_API_GATEWAY_URL + "gateway/feedback",{method: 'post',body: formData})
                .then(res => res.json())
                .then((result) => {
                    console.log(result);
                    var init = 0;
                    pushTagsToSAP();
                    //hide the model to correkt the bounding boxes because the user is done editing
                    UIkit.modal(document.getElementById("modal-full-split")).hide();
                    },(error) => {
                        UIkit.notification({message: 'Saving of feedback failed!', status: 'danger', pos: 'top-right', timeout: 5000});
                        console.error(error);
                        });

        }
        function pushTagsToSAP(){
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
                "FILECOMMENT":"edit",
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
                    window.location.reload();
                })
                .catch(error => console.log('error', error));
        }
    }
}


export default Model_correction;