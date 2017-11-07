var angular = require('angular');
require("angular-ui-router");
require("angular-chart.js");
require("angular-bootstrap");
require("checklist-model");
require("angular-chart");
require("ng-table");

require("d3");
require("c3");



var services = angular.module("services", []);
require("./services/report.service");
var dashboard = angular.module("dashboard", ["ui.router", "chart.js", "ui.bootstrap", "checklist-model", "angularChart", "ngTable", "services"]);
require("./controllers/home.controller");
require("./controllers/guideline.adherence.controller");
require("./controllers/main.check.controller");
require("./controllers/report.rate.controller");


dashboard.config(["$stateProvider", "$urlRouterProvider",
    function($stateProvider, $urlRouterProvider) {
        // $urlRouterProvider.otherwise("/reportingRate");
        $urlRouterProvider.when("", "/reportingRate");
        $stateProvider
            .state("home", {
                url: "",
                template: require("../views/main.html"),
                controller: "HomeController"
            }).state("home.reportingRate", {
                url: "/reportingRate",
                template: require("../views/reporting_rate.html")
            }).state("home.guidlineAdherenceRate", {
                url: "/guidlineAdherenceRate",
                template: require("../views/guidlineAdherenceRate.html")
            }).state("home.addTests", {
                url: "/addTests",
                template: require("../views/addTests.html")
            });
    }
]);

