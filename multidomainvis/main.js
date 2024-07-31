import * as THREE from 'three';

import {GUI} from './libs/lil-gui.module.min.js';
import {MapControls} from './libs/OrbitControls.js';
import {DataHandler} from './src/DataHandler.js';
import {DataSet} from './src/Dataset.js';
import {CSVLoader} from './src/CSVLoader.js';
import {XRButton} from './libs/XRButton.js';
import {XREstimatedLight} from './libs/XREstimatedLight.js'

let container;
let dolly, camera, scene, renderer;
let controls;

const parameters = {
    buildingOption: true,
    energy: true,
    noise: true,
    wind: true,
    radiation: true,
    option: "Option 1"
};

let dataSets;

// Uncomment this if you want to load a CityModel from a path in this directory
//const cityModelPath = '../Grasshopper Scripts/DTCC_CITYJSON_parser/CityModel.json'

// Paths loaded through web worker (CSVs) need to be
// relative to the worker directory (src/)
let dataSpecs = [
    {
        name: 'Option 0',
        noisePath: '../data/noise/option_0_Lden.csv',
        radiationPath: '../data/radiation/20230327_RadiationBaseCase.csv',
        windSurfaceCellPath: '../data/wind/Option_0/WindroseSurfaceCell_small.csv',
        windSurfaceNodesPath: '../data/wind/Option_0/WindroseSurfaceNodes_small.csv'
    },
    {
        name: 'Option 1',
        buildingOptionPath: './data/buildingOptions/option_1.stl',
        energyPath: './data/energy/alt_1.csv',
        noisePath: '../data/noise/option_1_Lden.csv',
        radiationPath: '../data/radiation/20230328_RadiationOption1_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_1/WindroseSurfaceCell_small.csv',
        windSurfaceNodesPath: '../data/wind/Option_1/WindroseSurfaceNodes_small.csv'
    },
    {
        name: 'Option 2',
        buildingOptionPath: './data/buildingOptions/option_2.stl',
        noisePath: '../data/noise/option_2_Lden.csv',
        radiationPath: '../data/radiation/20230328_RadiationOption2_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_2/WindroseSurfaceCell_small.csv',
        windSurfaceNodesPath: '../data/wind/Option_2/WindroseSurfaceNodes_small.csv'
    },
    {
        name: 'Option 3',
        buildingOptionPath: './data/buildingOptions/option_3.stl',
        noisePath: '../data/noise/option_3_Lden.csv',
        radiationPath: '../data/radiation/20230328_RadiationOption3_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_3/WindroseSurfaceCell_small.csv',
        windSurfaceNodesPath: '../data/wind/Option_3/WindroseSurfaceNodes_small.csv'
    },
    {
        name: 'Option 4',
        buildingOptionPath: './data/buildingOptions/option_4.stl',
        noisePath: '../data/noise/option_4_Lden.csv',
        radiationPath: '../data/radiation/20230328_RadiationOption4_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_4/WindroseSurfaceCell_small.csv',
        windSurfaceNodesPath: '../data/wind/Option_4/WindroseSurfaceNodes_small.csv'
    },
    {
        name: 'Option 5',
        buildingOptionPath: './data/buildingOptions/option_5.stl',
        noisePath: '../data/noise/option_5_Lden.csv',
        radiationPath: '../data/radiation/20230328_RadiationOption5_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_5/WindroseSurfaceCell_small.csv',
        windSurfaceNodesPath: '../data/wind/Option_5/WindroseSurfaceNodes_small.csv'
    },
    {
        name: 'Option 6',
        buildingOptionPath: './data/buildingOptions/option_6.stl',
        noisePath: '../data/noise/option_6_Lden.csv',
        radiationPath: '../data/radiation/20230328_RadiationOption6_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_6/WindroseSurfaceCell_small.csv',
        windSurfaceNodesPath: '../data/wind/Option_6/WindroseSurfaceNodes_small.csv'
    },
    {
        name: 'Option 7',
        buildingOptionPath: './data/buildingOptions/option_7.stl',
        noisePath: '../data/noise/option_7_Lden.csv',
        radiationPath: '../data/radiation/20230328_RadiationOption7_10mgrid.csv',
        windSurfaceCellPath: '../data/wind/Option_7/WindroseSurfaceCell_small.csv',
        windSurfaceNodesPath: '../data/wind/Option_7/WindroseSurfaceNodes_small.csv'
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

// Try to load the cityModel from the path declared above.
// If it doesn't work, ask the user to provide the file.
// The user may also ignore the missing file and continue.
try {
    // Load json from path
    fetch(cityModelPath)
        .then(response => response.json())
        .then(cityModelData => {
            console.log(`Loaded ${cityModelPath}`);
            init(cityModelData);
        }
    );
} catch (error) {
    const cityModelDialog = document.getElementById("cityModelDialog");
    const fileInput = document.getElementById("cityModelFile");
    const ignoreCityModelButton = document.getElementById("ignoreCityModelUpload");

    // Show the city model dialog
    cityModelDialog.style.display = 'block';

    // When a file is uploaded
    fileInput.onchange = () => {
        new Response(fileInput.files[0]).json().then(cityModelData => {
            cityModelDialog.style.display = 'none';
            console.log(`Loaded provided cityModel file`);
            init(cityModelData);
          }, err => {
            alert(`Could not parse the provided cityModel file:\n${err}`);
        });
    }

    // When the ignore button is clicked
    ignoreCityModelButton.onclick = () => {
        cityModelDialog.style.display = 'none';
        console.log("Ignoring missing cityModel file")
        init();
    }
}

function enableVR(scale, defaultLight) {
    renderer.xr.enabled = true;
    document.body.appendChild(XRButton.createButton(renderer, {optionalFeatures: ['light-estimation']}));
    renderer.setAnimationLoop(function () {
        renderer.render(scene, camera);
    } );

    //scene.background = new THREE.Color(0x00000,0);

    dolly = new THREE.Group();
    dolly.position.set(800, 10, -1000);
    dolly.position.multiplyScalar(scale);
    dolly.add(camera);
    scene.add(dolly);

    const xrLight = new XREstimatedLight(renderer);

    xrLight.addEventListener('estimationstart', () => {
        scene.add(xrLight);
        scene.remove(defaultLight);
        if (xrLight.environment) {
            scene.environment = xrLight.environment;
        }
    });

    xrLight.addEventListener('estimationend', () => {
        scene.add(defaultLight);
        scene.remove(xrLight);
        scene.environment = defaultEnvironment;
    });
}

function init(cityModelData) {
    const params = new URLSearchParams(window.location.search);
    const useVR = params.get('vr') !== null &&  params.get('vr') !== "false";
    let scale = params.get("scale");

    if (scale === null) {
        if (useVR) {
            scale = 1e-2;
        } else {
            scale = 1;
        }
    }

    container = document.getElementById('container');
    container.style = "background:none";

    renderer = new THREE.WebGLRenderer({antialias: true , alpha: true});
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);
    renderer.domElement.style = "background:none";

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 2000);


    let hemilight = new THREE.HemisphereLight(0x808080, 0x606060);
    hemilight.intensity = 3;

    const light = new THREE.DirectionalLight(0xffffff);
    light.position.set(0, 0, 0);
    light.target.position.set(830, 0, -1050);
    light.target.position.multiplyScalar(scale);
    light.intensity = 4;
    light.castShadow = true;
    light.shadow.radius = 32 * scale;
    light.shadow.camera.top = 300 * scale;
    light.shadow.camera.bottom = -300 * scale;
    light.shadow.camera.right = 300 * scale;
    light.shadow.camera.left = - 300 * scale;
    light.shadow.camera.far = 1300 * scale;
    light.shadow.mapSize.set(8192, 8192);

    light.target.updateMatrixWorld();
    light.shadow.camera.updateProjectionMatrix();

    let defaultLight = new THREE.Group();
    defaultLight.add(hemilight);
    defaultLight.add(light);
    defaultLight.position.set(700, 500, -1800);
    defaultLight.position.multiplyScalar(scale);
    scene.add(defaultLight);

    if (useVR) {
        enableVR(scale, defaultLight);
    } else {
        camera.position.set(915, 227, -1352);
        camera.position.multiplyScalar(scale);
    }

    controls = new MapControls(camera, renderer.domElement);
    controls.addEventListener('change', render);
    controls.maxPolarAngle = Math.PI * 0.495;
    controls.target.set(800, 50, -1000);
    controls.target.multiplyScalar(scale);
    controls.minDistance = 1.0 * scale;
    controls.maxDistance = 5000.0 * scale;
    controls.update();

    window.addEventListener('resize', onWindowResize);

    const dataHandler = new DataHandler(scene, scale);
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
            d.name, dataHandler, cityModelData, d.buildingOptionPath,
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


    // Don't show gui for ignored data
    const ignoredData = new URL(window.location.href).searchParams.getAll("ignoreData");
    const dataParams = ['buildingOption', 'energy', 'noise', 'radiation', 'wind'].filter(p=>!ignoredData.includes(p))

    const folderData = gui.addFolder('Data');
    for (let param of dataParams) {
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