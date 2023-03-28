import * as THREE from 'three';

import {GUI} from './libs/lil-gui.module.min.js';
import {MapControls} from './libs/OrbitControls.js';
import {Sky} from './libs/Sky.js';
import {STLLoader} from './libs/STLLoader.js';
import {DataHandler} from './src/DataHandler.js';
import { DataSet } from './src/Dataset.js';

let container;
let camera, scene, renderer;
let controls, sun;

const parameters = {
    elevation: 17,
    azimuth: 80,
    exposure: 0.7,
    buildingOption: true,
    energy: true,
    noise: true,
    wind: true,
    radiation: true,
    colorMap: 'rainbow',
    option: "Option 0"
};

let dataSets;

// Paths loaded through web worker (CSVs) need to be
// relative to the worker directory (src/)
const dataSpecs = [
    {
        name: 'Option 0',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        noisePath: '../data/noise/option_0_Lden.csv',
        radiationPath: '../data/radiation/20230327_RadiationBaseCase.csv',
        windSurfaceCellPath: '../data/wind/Option_0/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_0/WindroseSurfaceNodes.csv'
    },
    {
        name: 'Option 1',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        buildingOptionPath: './data/buildingOptions/option_1.stl',
        energyPath: './data/energy/alt_1.csv',
        noisePath: '../data/noise/option_1_Lden.csv',
        radiationPath: undefined,
        windSurfaceCellPath: '../data/wind/Option_1/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_1/WindroseSurfaceNodes.csv'
    },
    {
        name: 'Option 2',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        buildingOptionPath: './data/buildingOptions/option_2.stl',
        noisePath: '../data/noise/option_2_Lden.csv',
        windSurfaceCellPath: '../data/wind/Option_2/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_2/WindroseSurfaceNodes.csv'
    },
    {
        name: 'Option 3',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        buildingOptionPath: './data/buildingOptions/option_3.stl',
        noisePath: '../data/noise/option_3_Lden.csv',
        windSurfaceCellPath: '../data/wind/Option_3/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_3/WindroseSurfaceNodes.csv'
    },
    {
        name: 'Option 4',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        buildingOptionPath: './data/buildingOptions/option_4.stl',
        noisePath: '../data/noise/option_4_Lden.csv',
        windSurfaceCellPath: '../data/wind/Option_4/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_4/WindroseSurfaceNodes.csv'
    },
    {
        name: 'Option 5',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        buildingOptionPath: './data/buildingOptions/option_5.stl',
        noisePath: '../data/noise/option_5_Lden.csv',
        windSurfaceCellPath: '../data/wind/Option_5/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_5/WindroseSurfaceNodes.csv'
    },
    {
        name: 'Option 6',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        buildingOptionPath: './data/buildingOptions/option_6.stl',
        noisePath: '../data/noise/option_6_Lden.csv',
        windSurfaceCellPath: '../data/wind/Option_6/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_6/WindroseSurfaceNodes.csv'
    },
    {
        name: 'Option 7',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        buildingOptionPath: './data/buildingOptions/option_7.stl',
        noisePath: '../data/noise/option_7_Lden.csv',
        windSurfaceCellPath: '../data/wind/Option_7/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_7/WindroseSurfaceNodes.csv'
    }
]

init();

function init() {
    container = document.getElementById('container');

    renderer = new THREE.WebGLRenderer();
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    container.appendChild(renderer.domElement);


    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 20000);
    camera.position.set(700, 300, -1800);

    const axesHelper = new THREE.AxesHelper(5);
    scene.add(axesHelper);

    sun = new THREE.Vector3();
    const sky = new Sky();
    sky.scale.setScalar(10000);
    scene.add(sky);

    //const light = new THREE.PointLight(0xff0000, 1, 100);
    //light.position.set(800, 1000, -1000);
    //scene.add(light);

    const skyUniforms = sky.material.uniforms;

    skyUniforms['turbidity'].value = 10;
    skyUniforms['rayleigh'].value = 2;
    skyUniforms['mieCoefficient'].value = 0.005;
    skyUniforms['mieDirectionalG'].value = 0.8;

    const pmremGenerator = new THREE.PMREMGenerator(renderer);
    let renderTarget;

    function updateSun() {
        const phi = THREE.MathUtils.degToRad(90 - parameters.elevation);
        const theta = THREE.MathUtils.degToRad(parameters.azimuth);
        const exposure = parameters.exposure;
        sun.setFromSphericalCoords(1, phi, theta);
        sky.material.uniforms['sunPosition'].value.copy(sun);
        if (renderTarget !== undefined) renderTarget.dispose();
        renderTarget = pmremGenerator.fromScene(sky);
        renderer.toneMappingExposure = exposure;
        scene.environment = renderTarget.texture;
    }
    updateSun();

    controls = new MapControls(camera, renderer.domElement);
    controls.addEventListener('change', render);
    controls.maxPolarAngle = Math.PI * 0.495;
    controls.target.set(800, 50, -1000);
    controls.minDistance = 1.0;
    controls.maxDistance = 5000.0;
    controls.update();

    window.addEventListener('resize', onWindowResize);

    const dataHandler = new DataHandler(scene, parameters);

    let nLoadingDatasets = dataSpecs.length;
    dataSets = dataSpecs.map(d=>
        new DataSet(
            d.name, dataHandler, d.cityModelPath, d.buildingOptionPath,
            d.energyPath, d.noisePath, d.radiationPath,
            d.windSurfaceCellPath, d.windSurfaceNodesPath,
            dataset => {
                document.getElementById("loadingLog").innerHTML += `<li>${dataset.name} loaded</li>`;
                nLoadingDatasets--;
                dataset.setVisibility(parameters);
                if (nLoadingDatasets == 0) {
                    onDataLoaded()
                }
            }
        )
    );
}

function onDataLoaded() {
    console.log("All datasets loaded");
    render();

    const updateVisibilities = () => {
        for (let d of dataSets) {
            d.setVisibility(parameters);
            render();
        }
    };

    updateVisibilities();

    const gui = new GUI();
    gui.add(parameters, 'option', dataSpecs.map(d=>d.name)).onChange(updateVisibilities);

    const folderData = gui.addFolder('Data');
    for (let param of ['buildingOption', 'energy', 'noise', 'radiation', 'wind']) {
        folderData.add(parameters, param, true).onChange(updateVisibilities);
    }

    document.getElementById("overlay").style.display = "none";
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function render() {
    //const time = performance.now() * 0.001;
    console.log("Rendering")
    renderer.render(scene, camera);
}