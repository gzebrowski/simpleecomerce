"use strict";
var mainApp = angular.module("MainApp", []);

var calc_max_width_height = function(org_x, org_y, max_width, max_height)
{
    org_x = org_x * 1.0;
    org_y = org_y* 1.0;
    if (org_x / (max_width * 1.0) > (org_y / (max_height * 1.0))) {
        return _calc_max_width(org_x, org_y, max_width);
    }  else {
        return _calc_max_height(org_x, org_y, max_height);
    }
}

var _calc_max_width = function(org_x, org_y, max_width)
{
    return [max_width, parseInt(org_y / (org_x / (1.0 * max_width)))];
}

var _calc_max_height = function(org_x, org_y, max_height)
{
    return [parseInt(org_x / (org_y / (1.0 * max_height))), max_height];
}



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


mainApp.config(['$interpolateProvider', '$httpProvider', function($interpolateProvider, $httpProvider) {
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

.directive('myDraggable', ['$document', '$parse', function($document, $parse) {
  return {
    link: function(scope, element, attr) {
        var startX = 0, startY = 0, x = 0, y = 0, initX, initY;
        var obj = $parse(attr.myDraggable)(scope);
        initX = obj.left;
        initY = obj.top;
        element.on('mousedown', function(event) {
        // Prevent default dragging of selected content
            event.preventDefault();
            startX = event.pageX;
            startY = event.pageY;
            $document.on('mousemove', mousemove);
            $document.on('mouseup', mouseup);
        });

        function mousemove(event) {
            y = event.pageY - startY;
            x = event.pageX - startX;
            $parse(attr.myDraggable + '.top').assign(scope, y + initY);
            $parse(attr.myDraggable + '.left').assign(scope, x + initX);
            scope.$apply();
            /*
            element.css({
              top: y + 'px',
              left:  x + 'px'
            });
            */
        }

        function mouseup() {
            $document.off('mousemove', mousemove);
            $document.off('mouseup', mouseup);
            var obj = $parse(attr.myDraggable)(scope);
            initX = obj.left;
            initY = obj.top;
            scope.$apply();
        }
    }
  };
}])

.controller('MainCtrl', ['$scope', '$http', '$compile', '$window', '$timeout', '$parse', '$rootScope', function($scope, $http, $compile, $window, $timeout, $parse, $rootScope) {
	$scope.forms = {};
	$scope.inProggress = false;
    $scope.createCollection = function(name, defaultVal) {
        defaultVal = defaultVal || {items: {}, total: 0.0};
        $parse(name).assign($scope, defaultVal);
        return true;
    }
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
    $scope.textForm = {labelStyle: {top: 50, left: 50},
                       imgStyle: {style: {}}, cakeParams: {font_size: 16, font_color: '#000', font_type: 'Arial',
                       text_top: 50, text_left: 50}};

    $scope.uploatedFile = null;
    $scope.submitFile = function(element, formName, proggresSelector) {
        $scope.uploatedFile = null;
        var val = $(element).val();
        var progressBox = $(proggresSelector);
        $('form[name="' + formName + '"]').ajaxSubmit({
                beforeSubmit: function() {
                    progressBox.find(".progress-slide").width('0%');
                    progressBox.show();
                },
                uploadProgress: function(event, position, total, percentComplete){
                    progressBox.find(".progress-slide").width(percentComplete + '%');
                },
                success: function(data) {
                    var scope = $('form[name="' + formName + '"]').scope();
                    progressBox.hide();
                    switch (data.status) {
                        case 'OK':
                            $scope.uploatedFile = data.file_url;
                            $scope.uploatedFileSize = data.size;
                            $scope.textForm.cakeParams.image_url = data.file_key;
                            break;
                        case 'IMAGE_ERROR':
                            $scope.showAlert('Sorry, error when processed. Please choose another image');
                            break;
                        case 'TOO_SMALL':
                            $scope.showAlert('Error! Too small image. The size is: ' + data.size + ', minimum is: ' + data.minsize);
                            break;
                        case 'WRONG_FILE':
                            $scope.showAlert('Wrong file type. Only allowed types are: png, jpg, gif');
                            break;
                        case 'TOO_BIG':
                            $scope.showAlert('Too big file. Allowed maximum is:' + data.maxsize);
                            break;
                        }
                        scope.$apply();

                },
                resetForm: true,
                url: '/api/cake-composition/add/'
            });

    }
    $scope.submitFile2 = function(el, formName) {
        console.log(formName, el);
    }
    //---------------------------------------------------------------------

    $scope.getLabelStyle = function() {
        $scope.textForm.labelStyle.style = {
            'font-family': $scope.textForm.cakeParams.font_type,
            'font-size': $scope.textForm.cakeParams.font_size + 'px',
            color: $scope.textForm.cakeParams.font_color,
            top: $scope.textForm.labelStyle.top + 'px',
            left: $scope.textForm.labelStyle.left + 'px',
        }
        $scope.textForm.cakeParams.text_top = $scope.textForm.labelStyle.top;
        $scope.textForm.cakeParams.text_left = $scope.textForm.labelStyle.left;
        return $scope.textForm.labelStyle.style;
    }
    $scope.setFontStyle = function(prop, val, inc) {
        if (inc) {
            $scope.textForm.cakeParams[prop] = Math.max(0, val + inc);
        } else {
            $scope.textForm.cakeParams[prop] = val;
        }
    }
    $scope.getImageStyle = function() {
        var size = $scope.uploatedFileSize;
        if (size && (size[0] != $scope.textForm.imgStyle.imgWidth || size[1] != $scope.textForm.imgStyle.imgHeight)) {
            $scope.textForm.imgStyle.imgHeight = size[1];
            $scope.textForm.imgStyle.imgWidth = size[0];
            var container = $('.full-image-wrapper');
            var frameSizeW = container.width();
            var frameSizeH = container.height();
            container.find('.img-frame.space-horizontal').each(function() {
                frameSizeW -= $(this).width();
            })
            container.find('.img-frame.space-vertical').each(function() {
                frameSizeH -= $(this).height();
            })
            var newSize = calc_max_width_height(size[0], size[1], frameSizeW, frameSizeH);
            $scope.textForm.cakeParams.image_scale = newSize[0] / size[0];
            $scope.textForm.imgStyle.style.width = newSize[0];
            $scope.textForm.imgStyle.style.height = newSize[1];
        }
        return $scope.textForm.imgStyle.style || {};
    }

}])
