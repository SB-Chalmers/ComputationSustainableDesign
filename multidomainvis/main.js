import * as THREE from 'three';

import {GUI} from './libs/lil-gui.module.min.js';
import {MapControls} from './libs/OrbitControls.js';
import {Sky} from './libs/Sky.js';
import {DataHandler} from './src/DataHandler.js';
import {DataSet} from './src/Dataset.js';
import {CSVLoader} from './src/CSVLoader.js';

let container;
let camera, scene, renderer;
let controls, sun;

const parameters = {
    buildingOption: true,
    energy: true,
    noise: true,
    wind: true,
    radiation: true,
    option: "Option 0"
};

let dataSets;

// Paths loaded through web worker (CSVs) need to be
// relative to the worker directory (src/)
let dataSpecs = [
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
        radiationPath: '../data/radiation/20230328_RadiationOption1_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_1/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_1/WindroseSurfaceNodes.csv'
    },
    {
        name: 'Option 2',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        buildingOptionPath: './data/buildingOptions/option_2.stl',
        noisePath: '../data/noise/option_2_Lden.csv',
        radiationPath: '../data/radiation/20230328_RadiationOption2_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_2/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_2/WindroseSurfaceNodes.csv'
    },
    {
        name: 'Option 3',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        buildingOptionPath: './data/buildingOptions/option_3.stl',
        noisePath: '../data/noise/option_3_Lden.csv',
        radiationPath: '../data/radiation/20230328_RadiationOption3_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_3/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_3/WindroseSurfaceNodes.csv'
    },
    {
        name: 'Option 4',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        buildingOptionPath: './data/buildingOptions/option_4.stl',
        noisePath: '../data/noise/option_4_Lden.csv',
        radiationPath: '../data/radiation/20230328_RadiationOption4_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_4/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_4/WindroseSurfaceNodes.csv'
    },
    {
        name: 'Option 5',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        buildingOptionPath: './data/buildingOptions/option_5.stl',
        noisePath: '../data/noise/option_5_Lden.csv',
        radiationPath: '../data/radiation/20230328_RadiationOption5_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_5/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_5/WindroseSurfaceNodes.csv'
    },
    {
        name: 'Option 6',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        buildingOptionPath: './data/buildingOptions/option_6.stl',
        noisePath: '../data/noise/option_6_Lden.csv',
        radiationPath: '../data/radiation/20230328_RadiationOption6_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_6/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_6/WindroseSurfaceNodes.csv'
    },
    {
        name: 'Option 7',
        cityModelPath: '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json',
        buildingOptionPath: './data/buildingOptions/option_7.stl',
        noisePath: '../data/noise/option_7_Lden.csv',
        radiationPath: '../data/radiation/20230328_RadiationOption7_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_7/WindroseSurfaceCell.csv',
        windSurfaceNodesPath: '../data/wind/Option_7/WindroseSurfaceNodes.csv'
    }
]

document.addEventListener('keydown', (e) => {
    const dY = 0.1;
    if (e.code === "ArrowUp" || e.code === "ArrowDown") {
        for (let d of dataSets) {
            if (d) {
                for (let p of ['noise', 'radiation']) {
                    if (d.objects.has(p)) {
                        if (d.objects.get(p).visible) {
                            d.objects.get(p).position.y += (e.code === "ArrowDown" ? -1 : 1) * dY;
                            render();
                        }
                    }
                }
            }
        }
    }
  });

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

    const skyUniforms = sky.material.uniforms;

    skyUniforms['turbidity'].value = 10;
    skyUniforms['rayleigh'].value = 2;
    skyUniforms['mieCoefficient'].value = 0.005;
    skyUniforms['mieDirectionalG'].value = 0.8;

    const pmremGenerator = new THREE.PMREMGenerator(renderer);
    let renderTarget;

    const phi = THREE.MathUtils.degToRad(73);
    const theta = THREE.MathUtils.degToRad(80);
    const exposure = 0.7;
    sun.setFromSphericalCoords(1, phi, theta);
    sky.material.uniforms['sunPosition'].value.copy(sun);
    if (renderTarget !== undefined) renderTarget.dispose();
    renderTarget = pmremGenerator.fromScene(sky);
    renderer.toneMappingExposure = exposure;
    scene.environment = renderTarget.texture;

    controls = new MapControls(camera, renderer.domElement);
    controls.addEventListener('change', render);
    controls.maxPolarAngle = Math.PI * 0.495;
    controls.target.set(800, 50, -1000);
    controls.minDistance = 1.0;
    controls.maxDistance = 5000.0;
    controls.update();

    window.addEventListener('resize', onWindowResize);

    const dataHandler = new DataHandler(scene, parameters);
    const csvLoader = new CSVLoader(3);

    const searchParams = new URL(window.location.href).searchParams;

    // Filter options to include only those specified
    // with the "option" url parameter
    const includedOptions = searchParams.getAll("option");
    if (includedOptions.length > 0) {
        const includedOptionNames = includedOptions.map(i => `Option ${i}`);
        if (!includedOptionNames.includes(parameters.option)) {
            // Make sure we have a selected option
            parameters.option = includedOptionNames[0];
        }
        dataSpecs = dataSpecs.filter(d => includedOptionNames.includes(d.name))
    }

    const ignoreData = searchParams.getAll("ignoreData");
    for (let d of dataSpecs) {
        for (let dataSource of ignoreData) {
            if (dataSource == "wind") {
                delete d["windSurfaceCellPath"]
                delete d["windSurfaceNodesPath"]
            } else {
                delete d[dataSource+"Path"]
            }
        }
    }

    const loadingLog = document.getElementById("loadingLog");
    let nLoadingDatasets = dataSpecs.length;
    dataSets = dataSpecs.map(d=>
        new DataSet(
            d.name, dataHandler, d.cityModelPath, d.buildingOptionPath,
            d.energyPath, d.noisePath, d.radiationPath,
            d.windSurfaceCellPath, d.windSurfaceNodesPath,
            csvLoader,
            (dataset, path) => {
                loadingLog.innerHTML += `<li>${dataset.name} loaded ${path}</li>`;
            },
            dataset => {
                loadingLog.innerHTML += `<li><b>${dataset.name} fully loaded</b></li>`;
                nLoadingDatasets--;
                dataset.setVisibility(parameters);
                if (nLoadingDatasets == 0) {
                    onDataLoaded()
                    csvLoader.decommission();
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
    render();
}

function render() {
    renderer.render(scene, camera);
}