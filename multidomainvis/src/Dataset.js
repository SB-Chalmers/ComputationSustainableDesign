import * as THREE from 'three';
import {STLLoader} from '../libs/STLLoader.js';
import {loadCSV} from '../src/csvLoader.js';

async function getJSON(path) {
    return fetch(path)
        .then((response) => response.json())
        .then((responseJson) => {
            return responseJson
        });
}

class DataSet {
    constructor(name, dataHandler, cityModelPath,
        buildingOptionPath, energyPath, noisePath,
        radiationPath, windMesh, windLegend, windValuesPath,
        windValuesColumnName, onLoadingFinished
    ) {
        this.name = name;
        this.dataHandler = dataHandler;
        this.onLoadingFinished = onLoadingFinished;

        // Keep track of THREE objects and HTML legends
        this.objects = new Map();
        this.legends = new Map();

        if (windMesh) {
            this.objects.set("wind", windMesh);
        }
        if (windLegend) {
            this.legends.set("wind", windLegend);
        }

        // Keep track of files to load
        this.remainingLoads = [cityModelPath,
            buildingOptionPath, energyPath, noisePath,
            radiationPath, windValuesColumnName
        ].filter(path => path !== undefined);

        const loadRemainingData = cityOrigin => {
            this.loadBuildingOptionMesh(buildingOptionPath, cityOrigin);
            this.loadNoise(noisePath, cityOrigin);
            this.loadRadiation(radiationPath, cityOrigin);
            this.loadWindValues(windValuesPath, windValuesColumnName);
        }

        if (cityModelPath) {
            this.loadEnergy(energyPath, cityModelPath, loadRemainingData);
        } else {
            console.log(`No cityData provided`);
            const cityOrigin = new THREE.Vector2(319189, 6396991); // Taken from CityModel.json
            loadRemainingData(cityOrigin);
        }

    }

    logFinished(path) {
        const index = this.remainingLoads.indexOf(path);
        if (index > -1) {
            this.remainingLoads.splice(index, 1);
        }
        if (this.remainingLoads.length === 0) {
            console.log(`All loading finished for ${this.name}`);
            this.onLoadingFinished(this);
        }
    }

    setVisibility(parameters) {
        for (let p of ['buildingOption', 'energy', 'noise', 'radiation', 'wind']) {
            const visible = this.name == parameters['option'] && parameters[p];
            if (this.objects.has(p)) {
                if (p == 'wind' && this.windColorBuffer) {
                    const g = this.objects.get(p).geometry;
                    g.setAttribute('color',
                        visible ? this.windColorBuffer : this.defaultWindColorBuffer
                    );
                    g.attributes.color.needsUpdate = true;
                } else {
                    this.objects.get(p).visible = visible;
                }
                console.log(`${visible ? 'Showing':'Hiding'} ${p} object for ${this.name}.`);
            }
            if (this.legends.has(p)) {
                this.legends.get(p).style.display = visible ? 'block' : 'none';
                console.log(`${visible ? 'Showing':'Hiding'} ${p} legend for ${this.name}.`);
            }
        }
    }

    loadEnergy(energyPath, cityModelPath, callback) {
        if (!energyPath) {
            console.warn(`No energy data provided for ${this.name}`);
            getJSON(cityModelPath).then(j => {
                this.logFinished(cityModelPath);
                const energyMap = new Map();
                const cityOrigin = this.dataHandler.onCityDataLoaded(j, energyMap, this);
                callback(cityOrigin);
            });
            return;
        }
        // Need to know energy data first to color buildings
        Papa.parse(energyPath, {
            download: true, dynamicTyping: true, header: true,
            complete: results => {
                this.logFinished(energyPath);
                const energyMap = new Map();
                for (let row of results.data) {
                    energyMap.set(row.ID, row);
                }

                getJSON(cityModelPath).then(j => {
                    this.logFinished(cityModelPath);
                    const cityOrigin = this.dataHandler.onCityDataLoaded(j, energyMap, this);
                    callback(cityOrigin);
                });
            },
        });
    }

    loadBuildingOptionMesh(buildingOptionPath, cityOrigin) {
        if (!buildingOptionPath) {
            console.warn(`No buildingOption data provided for ${this.name}.`);
            return;
        }
        const loader = new STLLoader();
        loader.load(
            buildingOptionPath,
            geometry => {
                this.logFinished(buildingOptionPath);
                this.dataHandler.onBuildingOptionDataLoaded(
                    geometry, cityOrigin, this
                )
            }
        );
    }

    loadNoise(noisePath, cityOrigin) {
        if (!noisePath) {
            console.warn(`No noise data provided for ${this.name}.`);
            return;
        }
        loadCSV(noisePath, false, result => {
            this.logFinished(noisePath);
            this.dataHandler.onNoiseDataLoaded(result, cityOrigin, this);
        });
    }

    loadRadiation(radiationPath, cityOrigin) {
        if (!radiationPath) {
            console.warn(`No radiation data provided for ${this.name}.`);
            return;
        }
        loadCSV(radiationPath, true, result => {
            this.logFinished(radiationPath);
            this.dataHandler.onRadiationDataLoaded(result, cityOrigin, this);
        });
    }

    loadWindValues(lawsonLDDCPath, columnName) {
        if (!lawsonLDDCPath || !columnName) {
            console.warn(`No wind data provided for ${this.name}.`);
            return;
        }
        loadCSV(lawsonLDDCPath, true, result => {
            this.logFinished(columnName);
            this.dataHandler.onWindValueDataLoaded(result, columnName, this);
        })
    }
}

export {DataSet}