angular.module('dashboard').controller('MainChecksController', ['$scope',
    function($scope) {
        $scope.tests = [{
            "url": "orderFormFreeOfGaps",
            "desc": "NO BLANKS: If the facility reported, is the whole order form free of blanks?",
            "hasRegimen": false,
            "hasChart": true,
            "testNumber": 3,
            "template": "/static/views/chart.html"
        }, {
            "url": "facilitiesMultiple",
            "desc": "DUPLICATE ORDERS: Facilities that submitted more than one order over the cycle",
            "hasRegimen": false,
            "hasChart": false,
            "hasCycle": true,
            "testNumber": 4,
            "template": "/static/views/table.html"
        }, {
            "url": "orderFormFreeOfNegativeNumbers",
            "desc": "NO NEGATIVES: Is the order free of negative numbers?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 5,
            "template": "/static/views/chart.html"
        }, {
            "url": "consumptionAndPatients",
            "desc": "CONSUMPTION AND PATIENTS: Do consumption volumes tally with corresponding patient regimen volumes (i.e. they are within 30% of each other)?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 6,
            "template": "/static/views/chart.html"
        }, {
            "url": "differentOrdersOverTime",
            "desc": "NON-REPEATING ORDERS: Does the facility avoid repeating the same orders in consecutive cycles?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 7,
            "template": "/static/views/chart.html"
        }, {
            "url": "closingBalance",
            "desc": "Does Opening  balance of the cycle = Closing balance from the previous one?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 8,
            "template": "/static/views/chart.html"
        }, {
            "url": "stableConsumption",
            "desc": "STABLE CONSUMPTION: Is total consumption stable from one cycle to the next (i.e. less than 50% growth or decline from one cycle to the next)?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 9,
            "template": "/static/views/chart.html"
        }, {
            "url": "stablePatientVolumes",
            "desc": "STABLE PATIENT VOLUMES: Are total patient numbers stable from one cycle to the next?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 11,
            "template": "/static/views/chart.html"
        }, {
            "url": "warehouseFulfilment",
            "desc": "WAREHOUSE FULFILMENT: Does volume ordered = volume delivered in following cycle?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 10,
            "template": "/static/views/chart.html"
        }, {
            "url": "nnrtiCurrentAdults",
            "desc": "NRTI vs NNRTI/PI VOLUMES (CURRENT ADULTS): Do total current Adult NRTI patient volumes tally with total NNRTI & PI patient volumes?",
            "hasRegimen": false,
            "hasChart": true,
            "testNumber": 15,
            "template": "/static/views/chart.html"
        }, {
            "url": "nnrtiCurrentPaed",
            "desc": "NRTI vs NNRTI/PI VOLUMES (CURRENT PAED): Do total current Paed NRTI patient volumes tally with total NNRTI & PI patient volumes?",
            "hasRegimen": false,
            "hasChart": true,
            "testNumber": 16,
            "template": "/static/views/chart.html"
        }, {
            "url": "nnrtiNewAdults",
            "desc": "NRTI vs NNRTI/PI VOLUMES (ESTIMATED NEW ADULTS): Do total Estimated New Adult NRTI patient volumes tally with total NNRTI & PI patient volumes?",
            "hasRegimen": false,
            "hasChart": true,
            "testNumber": 17,
            "template": "/static/views/chart.html"
        }, {
            "url": "nnrtiNewPaed",
            "desc": "NRTI vs NNRTI/PI VOLUMES (ESTIMATED NEW PAED): Do total Estimated New Paed NRTI patient volumes tally with total NNRTI & PI patient volumes?",
            "hasRegimen": false,
            "hasChart": true,
            "testNumber": 18,
            "template": "/static/views/chart.html"
        }];
        $scope.regimens = [{
            name: "TDF/3TC/EFV (Adult)",
            value: "TDF/3TC/EFV"
        }, {
            name: "ABC/3TC (Paed)",
            value: "ABC/3TC"
        }, {
            name: "EFV200 (Paed)",
            value: "EFV200 (Paed)"
        }];
        $scope.selectedRegimen = $scope.regimens[0];

        $scope.selectedTest = $scope.tests[0];

    }
]);
angular.module('dashboard').controller('MultipleOrdersController', ['$scope', 'ReportService', 'NgTableParams',
    function($scope, ReportService, NgTableParams) {
        var updateData = function() {
            ReportService.getDataForTest('facilitiesMultiple', {
                'cycle': $scope.selectedCycle
            }).then(function(data) {
                var values = data.values;
                $scope.tableParams = new NgTableParams({
                    page: 1,
                    count: 10
                }, {
                    filterDelay: 0,
                    counts: [],
                    data: values
                });
            });
        }

        updateData();

        $scope.$watch('selectedCycle', function() {
            updateData();
        }, true);


    }
]);
angular.module('dashboard').controller('LineChartController', ['$scope', 'ReportService',
    function($scope, ReportService) {
        var update = function(start, end) {
            var test = $scope.selectedTest.url;
            var regimen = undefined;
            if ($scope.selectedRegimen) {
                regimen = $scope.selectedRegimen.value;
            }
            ReportService.getDataForTest(test, {
                start: start,
                end: end,
                regimen: regimen
            }).then(function(data) {
                var values = data.values;
                $scope.options = {
                    data: values,
                    chart: {
                        axis: {
                            y: {
                                max: 100,
                                min: 0,
                                padding: {
                                    top: 0,
                                    bottom: 0
                                }
                            }
                        }
                    },
                    dimensions: {
                        cycle: {
                            axis: 'x',
                            type: 'line'
                        },
                        no: {
                            axis: 'y',
                            type: 'line',
                            name: 'Fail',
                            color: 'red',
                            dataType: 'numeric',
                            displayFormat: d3.format(".1f")
                        },
                        yes: {
                            axis: 'y',
                            type: 'line',
                            name: 'Pass',
                            color: '#27ae60',
                            dataType: 'numeric',
                            displayFormat: d3.format(".1f")
                        },
                        not_reporting: {
                            axis: 'y',
                            type: 'line',
                            color: 'gray',
                            name: 'Insufficient Data',
                            dataType: 'numeric',
                            displayFormat: d3.format(".1f")
                        }
                    }
                };
            });


        };
        $scope.$watch('startCycle', function(start) {
            if (start && $scope.selectedTest) {
                update($scope.startCycle, $scope.endCycle);
            }

        }, true);

        $scope.$watch('endCycle', function(end) {
            if (end && $scope.selectedTest) {
                update($scope.startCycle, $scope.endCycle);
            }

        }, true);

        $scope.$watch('selectedTest', function(test) {
            if (test) {
                update($scope.startCycle, $scope.endCycle);
            }

        }, true);

        $scope.$watch('selectedRegimen', function(regimen) {
            if (regimen) {
                update($scope.startCycle, $scope.endCycle);
            }

        }, true);
    }
]);