import * as THREE from 'three';
import {STLLoader} from '../libs/STLLoader.js';

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
        radiationPath, windSurfaceCellPath, windSurfaceNodesPath, csvLoader,
        onLoadingUpdate, onLoadingFinished
    ) {
        this.name = name;
        this.dataHandler = dataHandler;
        this.onLoadingUpdate = onLoadingUpdate;
        this.onLoadingFinished = onLoadingFinished;

        this.csvLoader = csvLoader;

        // Keep track of THREE objects and HTML legends
        this.objects = new Map();
        this.legends = new Map();

        // Keep track of files to load
        this.remainingLoads = [];
        if (buildingOptionPath) {
            this.remainingLoads.push('buildingOption');
        }
        if (energyPath) {
            this.remainingLoads.push('energy');
        }
        if (noisePath) {
            this.remainingLoads.push('noise');
        }
        if (radiationPath) {
            this.remainingLoads.push('radiation');
        }
        if (windSurfaceCellPath && windSurfaceNodesPath) {
            this.remainingLoads.push('wind');
        }

        const loadRemainingData = cityOrigin => {
            this.loadBuildingOptionMesh(buildingOptionPath, cityOrigin);
            this.loadNoise(noisePath, cityOrigin);
            this.loadRadiation(radiationPath);
            this.loadWindSurface(windSurfaceCellPath, windSurfaceNodesPath, cityOrigin);
        }

        if (cityModelPath) {
            this.loadEnergy(energyPath, cityModelPath, loadRemainingData);
        } else {
            console.log(`No cityData provided`);
            const cityOrigin = new THREE.Vector2(319189, 6396991); // Taken from CityModel.json
            loadRemainingData(cityOrigin);
        }

    }

    logFinished(key) {
        const index = this.remainingLoads.indexOf(key);
        if (index > -1) {
            this.remainingLoads.splice(index, 1);
        }
        this.onLoadingUpdate(this, key);
        if (this.remainingLoads.length === 0) {
            console.log(`All loading finished for ${this.name}`);
            this.onLoadingFinished(this);
        }
    }

    setVisibility(parameters) {
        for (let p of ['buildingOption', 'energy', 'noise', 'radiation', 'wind']) {
            const visible = this.name == parameters['option'] && parameters[p];
            if (this.objects.has(p)) {
                this.objects.get(p).visible = visible;
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
                const energyMap = new Map();
                const cityOrigin = this.dataHandler.onCityDataLoaded(j, energyMap, (mesh, colorbar) => {
                    this.objects.set('energy', mesh);
                    if (colorbar) {
                        this.legends.set('energy', colorbar);
                    }
                    this.logFinished('energy');
                });
                callback(cityOrigin);
            });
            return;
        }
        // Need to know energy data first to color buildings
        Papa.parse(energyPath, {
            download: true, dynamicTyping: true, header: true,
            complete: results => {
                const energyMap = new Map();
                for (let row of results.data) {
                    energyMap.set(row.ID, row);
                }

                getJSON(cityModelPath).then(j => {
                    const cityOrigin = this.dataHandler.onCityDataLoaded(j, energyMap, (mesh, colorbar) => {
                        this.objects.set('energy', mesh);
                        this.legends.set('energy', colorbar);
                        this.logFinished('energy');
                    });
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
                this.dataHandler.onBuildingOptionDataLoaded(
                    geometry, cityOrigin, mesh => {
                        this.objects.set('buildingOption', mesh);
                        this.logFinished('buildingOption');
                    }
                )
            }
        );
    }

    loadNoise(noisePath, cityOrigin) {
        if (!noisePath) {
            console.warn(`No noise data provided for ${this.name}.`);
            return;
        }
        this.csvLoader.loadCSV(noisePath, false, result => {
            this.dataHandler.onNoiseDataLoaded(result, cityOrigin, (mesh, colorbar) => {
                this.legends.set('noise', colorbar);
                this.objects.set('noise', mesh);
                this.logFinished('noise');
            });
        });
    }

    loadRadiation(radiationPath) {
        if (!radiationPath) {
            console.warn(`No radiation data provided for ${this.name}.`);
            return;
        }
        this.csvLoader.loadCSV(radiationPath, true, result => {
            this.dataHandler.onRadiationDataLoaded(result, this, (mesh, colorbar) => {
                this.objects.set('radiation', mesh);
                this.legends.set('radiation', colorbar);
                this.logFinished('radiation');
            });
        });
    }

    loadWindSurface(windSurfaceCellPath, windSurfaceNodesPath, cityOrigin) {
        if (!windSurfaceCellPath || !windSurfaceNodesPath) {
            console.warn(`No wind data provided for ${this.name}.`);
            return;
        }
        let cellResults, nodeResults;

        const onBothLoaded = () => {
            this.dataHandler.onWindDataLoaded(cellResults, nodeResults, cityOrigin, (mesh, colorbar) => {
                this.objects.set('wind', mesh);
                this.legends.set('wind', colorbar);
                this.logFinished('wind');
            });
        }

        this.csvLoader.loadCSV(windSurfaceCellPath, true, result => {
            cellResults = result;
            if (nodeResults) {
                onBothLoaded();
            }
        });

        this.csvLoader.loadCSV(windSurfaceNodesPath, true, result => {
            nodeResults = result;
            if (cellResults) {
               onBothLoaded();
            }
        });
    }
}

export {DataSet}