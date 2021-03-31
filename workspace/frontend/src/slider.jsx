import React, { Component } from 'react'
import BeforeAfterSlider from 'react-before-after-slider'
//import after from '../public/after_detection.jpg';
//import before from '../public/before_detection.jpg';

class Slider extends React.Component {
    render() {
        //const before = 'https://images.unsplash.com/photo-1472214103451-9374bd1c798e?ixlib=rb-0.3.5&s=9a6ae0224c196441b4b78931c0bf78ba&auto=format&fit=crop&w=3900&q=80'
        //const after = 'https://images.unsplash.com/photo-1429593886847-3cc52983f919?ixlib=rb-0.3.5&s=24b2827bd767197c78641f9993e51a58&auto=format&fit=crop&w=3789&q=80'
        //const content = document.getElementById('styles_handle__33IZp').innerHTML += "<i data-v-2aa9daa6='' aria-hidden='true' className='fa fa-angle-right'>nothing</i>" + "<i data-v-2aa9daa6='' aria-hidden='true' className='fa fa-angle-left'>nothing</i>";
        return (
            <BeforeAfterSlider
                before={process.env.PUBLIC_URL + '/before_detection.png'}
                after={process.env.PUBLIC_URL + '/after_detection.png'}
                width={640}
                height={480}
            />
        )
    }
}


export default Slider;