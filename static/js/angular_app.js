"use strict";
var ecommerceApp = angular.module("EcommerceApp", []);

$(document).ready(function() {
    $('[data-open2]').click(function(){ $('#' + $(this).attr('data-open2')).foundation('open');})
});

function convertDateTime(date, time){
    var dt = date.split("-").map(function(x) { return parseInt(x);});
    var tm = time.split(":");
    return new Date(dt[0], dt[1] - 1, dt[2], tm[0], tm[1]);
}

function showModal(el) {
    $(el).foundation('open');
}


ecommerceApp.config(['$interpolateProvider', '$httpProvider', function($interpolateProvider, $httpProvider) {
    /* for Django templates */
    $interpolateProvider.startSymbol('{!');
    $interpolateProvider.endSymbol('!}');
    /* for rest api */
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}])
.directive('showAdminUrl', ['$parse', function($parse) {
    return {
        restrict: 'A',
        link: function(scope, el, attrs) {
            if (attrs.showAdminUrl) {
                el.prepend($('<a />').attr('href', attrs.showAdminUrl).addClass('staff-edit-content').text('edit'));
            }
        }
    }
}])
.filter('unsafe', ['$sce', function($sce) { return $sce.trustAsHtml; }])
.filter('stripprotocol', function() { return function(val) {
    return val.replace(/^https?:/i, '');
} })
.directive('validCondition', ['$parse', function($parse) {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function(scope, el, attrs, c) {
            scope.$watch(attrs.validCondition, function(val) {
                var k, cond = scope.$eval(attrs.validCondition);
                for (k in cond) {
                    c.$setValidity(k, !cond[k]);
                }
            });
        }
    }
}])
.directive('fieldRequired', [function() {
    return {
        restrict: 'C',
        link: function(scope, el, attrs) {
            el.find('input, select, textarea').prop('required', true).attr('required', 'required');
        }
    }
}])

.controller('EcommerceCtrl', ['$scope', '$http', '$compile', '$window', '$timeout', '$parse', '$rootScope', function($scope, $http, $compile, $window, $timeout, $parse, $rootScope) {
	$scope.forms = {};
	$scope.inProggress = false;
    $scope.showAlert = function (message) {
        $rootScope.alertMessage = message;
        $timeout(function() {$window.showModal('#alert-message');}, 0);
    }

	$scope.storeData = function(data, key) {
        var repr = angular.toJson(data);
        sessionStorage.setItem(key, repr);
	}
	$scope.restoreData = function(key) {
        var val = sessionStorage.getItem(key);
        return (val) ? angular.fromJson(val) : null;
	}
    $scope.basket = $scope.restoreData('basket') || {items: {}, total: 0.0};
    $scope.createCollection = function(name, defaultVal) {
        defaultVal = defaultVal || {items: {}, total: 0.0};
        $parse(name).assign($scope, defaultVal);
        return true;
    }
    $scope.registredProducts = [];
    $scope.registerProduct = function(model, value) {
        $parse(model).assign($scope, value);

        if ($scope.registredProducts.indexOf(model) == -1) {
            $scope.registredProducts.push(model);
        }
    }
    $scope.changeValue = function(model, val) {
        var currVal = parseInt($parse(model)($scope));

        $parse(model).assign($scope, Math.max(1, currVal + val));
    }
    $scope.orderProduct = function(key, name, image, price, quantity) {
        $scope.basket.items[key] = {key: key, name: name, image: image, price: price, quantity: quantity || 1};
        $scope.updateBasket();
    }
    $scope.updateBasket = function() {
        var total = 0;
        angular.forEach($scope.basket.items, function(value, key) {
            total += parseFloat(value.price) * parseInt(value.quantity);
        })
        $scope.basket.total = total;
        $scope.storeData($scope.basket, 'basket');
    }
    $scope.removeProduct = function(event, key) {
        if ($scope.basket.items[key]) {
            delete $scope.basket.items[key]
        }
        $scope.updateBasket();
        event.stopPropagation();
        return false;
    }
    $scope.doCheckout = function(event, form, data) {
        var frm = $parse(form)($scope);
        if (frm.$valid && $scope.basket.total) {
            $scope.inProggress = true;
            var items = [];
            angular.forEach($scope.basket.items, function(value, key) {
                items.push(value.key + ':' + value.quantity);
            })
            items = items.join(';');
            data.items = items;
            $http.post('/api/order/add/', data).success(function(data2){
                $scope.inProggress = false;
                $scope.basket = {items: {}, total: 0.0};
                $scope.updateBasket();
                $scope.showAlert('Your order has been sent. Thank you!');
            })
        }
        event.stopPropagation();
        return false;
    }
    $scope.tooEarly = function(dt, tm) {
        if (dt && tm) {
            var date = convertDateTime(dt, tm);
            var tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            if (date <= tomorrow) {
                return true;
            }
        }
        return false;
    }
}])
