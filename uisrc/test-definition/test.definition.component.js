var testTypes = require("./test.types");
var testDefinitionController = ["$scope", "metadataService", "previewService", function ($scope, metadataService, preview) {
    var ctrl = this;

    ctrl.setMultiplicationFactors = function (has_factors, group) {
        if (has_factors && !group.factors) {
            group.factors = {};
            group.selected_fields.forEach(function (field) {
                group.factors[field] = 1;
            });
        }
    };

    ctrl.previewDefinition = function (definition) {
        preview.show(definition);
    };

    ctrl.setInitialModel = function (testType) {
        if (ctrl.definition.groups) {
            ctrl.definition.groups.forEach(function (group) {
                group.model = testType.models[0];
            });
        }
    };

    ctrl.reset = function () {
        ctrl.definition = {type: testTypes.FacilityTest(ctrl.metaData), operatorConstant: 1.0};
        var testType = ctrl.definition.type;
        ctrl.definition.groups = testType.getGroups(ctrl.metaData);
    };

    var init = function () {
        metadataService.getAllFields().then(function (metaData) {
            ctrl.metaData = metaData;
            ctrl.testTypes = [
                testTypes.FacilityTest(metaData),
                testTypes.FacilityTestWithTracingFormulation(metaData)
            ];
            if (ctrl.value) {
                ctrl.definition = testTypes.buildDefinition(ctrl.value, metaData);
            } else {
                ctrl.reset();
            }
        });
    };

    init();

    return ctrl;
}];
module.exports = testDefinitionController;