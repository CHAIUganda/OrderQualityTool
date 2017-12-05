module.exports = ["$scope", "metadataService", "ngDialog", function ($scope, metadataService, ngDialog) {
    var ctrl = this;
    ctrl.testTypes = [
        {id: "FacilityOnly", name: "Facility Only"},
        {id: "FacilityAndSampleFormulation", name: "Facility And Sample Formulation"}
    ];
    ctrl.cycles = [
        {id: "Current", name: "Current Cycle"},
        {id: "Next", name: "Next Cycle"},
        {id: "Previous", name: "Previous Cycle"},
    ];
    ctrl.calculations = [
        {id: "SUM", name: "Sum"},
        {id: "AVG", name: "Average"}
    ];

    ctrl.models = [
        {id: "Adult", name: "Adult Records"},
        {id: "Paed", name: "Paed Records"},
        {id: "Consumption", name: "Consumption Records"}
    ];
    var newGroup = function () {
        var next_group_number = ctrl.definition.groups.length + 1;
        return {
            cycle: ctrl.cycles[0],
            model: ctrl.models[0],
            aggregation: ctrl.calculations[0],
            selected_consumption_fields: [],
            selected_formulations: [],
            name: "G" + next_group_number
        };
    };

    ctrl.main_regex = /^(G\d) (>|<|(?:<=)|(?:>=)|==|\*) ((?:\d+\.?\d*|\.\d+)|G\d) ?(?: ?(\s|>|<|<=|>=|==) ?((?:\d+\.?\d*|\.\d*)|G\d)?)?$/g;

    ctrl.newGroup = newGroup;
    ctrl.previewDefinition = function (definition) {
        metadataService.previewDefinition(definition).then(function (preview) {
            ngDialog.open({
                template: require('./preview.html'),
                plain: true,
                closeByDocument: false,
                controller: ["$scope", "preview", function Ctrl($scope, preview) {
                    var init = function (thePreview) {
                        $scope.cycle = thePreview.sample_cycle;
                        $scope.location = thePreview.sample_location;
                        $scope.cycles = thePreview.cycles;
                        $scope.locations = thePreview.locations;
                        $scope.groups = thePreview.groups;
                    };
                    init(preview);

                    $scope.update = function (cycle, location) {

                        definition.sample = {cycle: cycle, location: location};
                        metadataService.previewDefinition(definition).then(function (preview) {
                            init(preview);
                        })
                    }

                }],
                resolve: {
                    preview: function getPreview() {
                        return preview;
                    }
                }
            });
        })
    };
    ctrl.addGroup = function () {
        var group = newGroup();
        ctrl.definition.groups.push(group);
        var lastIndex = ctrl.definition.groups.length - 1;
        ctrl.setFields(lastIndex, group.model)
    };

    ctrl.removeGroup = function (group) {
        ctrl.definition.groups.pop(group);
    };

    ctrl.setFields = function (index, model) {
        if (!model) {
            return;
        }
        if (model.id === "Adult" || model.id === "Paed") {
            ctrl.fields[index] = ctrl.patient_fields;

        }
        if (model.id === "Adult") {
            ctrl.formulations[index] = ctrl.formulations_adult;
        }
        if (model.id === "Paed") {
            ctrl.formulations[index] = ctrl.formulations_paed;

        }
        if (model.id === "Consumption") {
            ctrl.fields[index] = ctrl.consumption_fields;
            ctrl.formulations[index] = ctrl.formulations_consumption;
        }


    };

    function init() {
        metadataService.getAllFields().then(function (data) {
            ctrl.fields = [];
            ctrl.formulations = [];
            ctrl.consumption_fields = data.consumption_fields;
            ctrl.patient_fields = data.patient_fields;
            ctrl.formulations_adult = data.formulations_adult;
            ctrl.formulations_paed = data.formulations_paed;
            ctrl.formulations_consumption = data.formulations_consumption;


            if (ctrl.value) {
                var definition = JSON.parse(ctrl.value);
                for (var index = 0; index < definition.groups.length; index++) {
                    var group = definition.groups[index];
                    ctrl.setFields(index, group.model);
                }
                ctrl.definition = definition;

            } else {
                ctrl.definition = {type: ctrl.testTypes[0], operatorConstant: 1};
                ctrl.definition.groups = [];
                ctrl.addGroup();
                ctrl.addGroup();
            }
        });
    }

    ctrl.reset = function () {
        ctrl.definition = {type: ctrl.testTypes[0], operatorConstant: 1.0};
        ctrl.definition.groups = [];
        ctrl.addGroup();
        ctrl.addGroup();
    };

    init();

    return ctrl;
}];