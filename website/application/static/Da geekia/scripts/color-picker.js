var app = angular.module("app", []);

app.controller("startCtrl", function($scope) {
  $scope.color = "rgba(135, 86, 255, 1)";
  $scope.color2 = "rgba(112, 255, 253, 1)";
  $scope.test = function() {};
});

app.directive("cpick", function() {
  function link(scope, element, attrs, ngModel) {
    if (!ngModel) return;
    scope.transparency = 1;
    scope.brightness = 0;
    scope.red = 0;
    scope.green = 0;
    scope.blue = 0;
    scope.hex = "#000";
    scope.grayscale = [
      "rgba(255,255,255,1)",
      "rgba(200,200,200,1)",
      "rgba(150,150,150,1)",
      "rgba(100,100,100,1)",
      "rgba(50,50,50,1)",
      "rgba(0,0,0,1)"
    ];
    scope.presets = [
      "rgba(255, 82, 92, 1)",
      "rgba(247, 51, 255, 1)",
      "rgba(135, 86, 255, 1)",
      "rgba(123, 172, 255, 1)",
      "rgba(112, 255, 253, 1)",
      "rgba(147, 255, 159, 1)",
      "rgba(255, 244, 89, 1)",
      "rgba(255, 157, 74, 1)"
    ];
    var canvas = element.find("#color-canvas")[0],
      module = element.find(".cpick-module")[0],
      canvaswrapper = element.find(".cpick")[0],
      previewEl = element.find(".cpick-preview")[0],
      indicatorEl = element.find(".cpick-indicator")[0],
      transparencyEl = element.find(".cpick-transparency")[0],
      darknessEl = element.find(".darkness")[0],
      brightnessEl = element.find(".cpick-brightness")[0],
      brightIndicatorEl = element.find(".cpick-brightness-indicator")[0],
      transIndicatorEl = element.find(".cpick-transparency-indicator")[0],
      ctx = canvas.getContext("2d");

    var cdown = false,
      tdown = false,
      bdown = false,
      updateModel = false;

    function drawBg() {
      canvas.width = canvaswrapper.offsetWidth;
      canvas.height = canvaswrapper.offsetHeight;
      var image = new Image(),
        url =
          "http://jonathanhagglund.se/projects/codepen-assets/cwheeltintcrop.png";
      image.src = url + "?" + new Date().getTime();
      image.setAttribute("crossOrigin", "");
      image.onload = function() {
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
      };
    }
    function setBrightness(bright) {
      var brightH = angular.element(brightnessEl)[0].offsetHeight;
      var brightY = brightH * bright;
      scope.brightness = bright;
      angular.element(brightIndicatorEl).css({
        top: brightY.toFixed(2) + "px",
        bottom: "auto"
      });
    }
    function changeBrightness(e) {
      if (bCanPreview && bdown) {
        // get coordinates of current position
        var brightY = Math.floor(
          e.pageY - angular.element(brightnessEl).offset().top
        );
        var brightH = angular.element(brightnessEl)[0].offsetHeight;
        var bright = (brightY / brightH) * 1;
        angular.element(brightIndicatorEl).css({
          top: brightY.toFixed(2) + "px",
          bottom: "auto"
        });
        colorUpdate(false, false, false, false, bright);
      }
    }
    function setTransparency(trans) {
      var transH = angular.element(transparencyEl)[0].offsetHeight;
      var transY = transH * trans;
      angular.element(transIndicatorEl).css({
        top: transY.toFixed(2) + "px",
        bottom: "auto"
      });
    }
    function changeTransparency(e) {
      if (bCanPreview && tdown) {
        // get coordinates of current position
        var transY = Math.floor(
          e.pageY - angular.element(transparencyEl).offset().top
        );
        var transH = angular.element(transparencyEl)[0].offsetHeight;
        var trans = (transY / transH) * 1;
        angular.element(transIndicatorEl).css({
          top: transY + "px",
          bottom: "auto"
        });
        colorUpdate(false, false, false, trans);
      }
    }

    scope.rgbaStringToUpdate = function(rgba) {
      console.log(rgba);
      setBrightness(0);
      rgba = rgba
        .substring(rgba.indexOf("(") + 1, rgba.lastIndexOf(")"))
        .split(/,\s*/);
      colorUpdate(rgba[0], rgba[1], rgba[2], rgba[3]);
      setTransparency(rgba[3]);
    };

    function shadeRGBColor(color, percent) {
      var f = color.split(","),
        t = percent < 0 ? 0 : 255,
        p = percent < 0 ? percent * -1 : percent,
        R = parseInt(f[0].slice(4)),
        G = parseInt(f[1]),
        B = parseInt(f[2]);
      //return "rgba("+(Math.round((t-R)*p)+R)+", "+(Math.round((t-G)*p)+G)+", "+(Math.round((t-B)*p)+B)+", "+scope.transparency+")";
      return {
        red: Math.round((t - R) * p) + R,
        green: Math.round((t - G) * p) + G,
        blue: Math.round((t - B) * p) + B
      };
    }
    function colorUpdate(r, g, b, a, d) {
      if (r) {
        scope.red = r;
      }
      if (g) {
        scope.green = g;
      }
      if (b) {
        scope.blue = b;
      }
      if (a) {
        scope.transparency = a;
      }
      if (d) {
        scope.brightness = d;
      }
      // update preview color
      var rgb =
        "rgb(" + scope.red + ", " + scope.green + ", " + scope.blue + ")";
      var rgba =
        "rgba(" +
        scope.red +
        ", " +
        scope.green +
        ", " +
        scope.blue +
        ", " +
        scope.transparency +
        ")";
      var darkness = shadeRGBColor(rgb, -scope.brightness);
      var drgb =
        "rgb(" +
        darkness.red +
        ", " +
        darkness.green +
        ", " +
        darkness.blue +
        ")";
      var drgba =
        "rgba(" +
        darkness.red +
        ", " +
        darkness.green +
        ", " +
        darkness.blue +
        "," +
        scope.transparency +
        ")";
      angular.element(transparencyEl).css({
        background:
          "-moz-linear-gradient(top, rgba(50,50,50,0) 0%, " + drgb + " 100% )",
        background:
          "-webkit-linear-gradient(top, rgba(50,50,50,0) 0%, " +
          drgb +
          " 100% )",
        background:
          "linear-gradient(to bottom, rgba(50,50,50,0) 0%, " + drgb + " 100% )",
        filter:
          "progid:DXImageTransform.Microsoft.gradient( startColorstr='#000222', endColorstr='#001e5799',GradientType=0 )"
      });
      angular.element(brightnessEl).css({
        background: "-moz-linear-gradient(top, " + rgb + " 0%, #000 100%)",
        background: "-webkit-linear-gradient(top, " + rgb + " 0%, #000 100%)",
        background: "linear-gradient(to bottom, " + rgb + " 0%, #000 100%)",
        filter:
          "progid:DXImageTransform.Microsoft.gradient( startColorstr='#000222', endColorstr='#001e5799',GradientType=0 )"
      });
      angular.element(previewEl).css({ "background-color": "transparent" });
      angular.element(previewEl).css({ cursor: "context-menu" });
      canvaswrapper.style.opacity = scope.transparency;
      darknessEl.style.opacity = scope.brightness;
      var dColor = scope.blue + 256 * scope.green + 65536 * scope.red;
      scope.hex = "#" + ("0000" + dColor.toString(16)).substr(-6);
      console.log(scope.hex);
      document.getElementById("colore-scelto").value = scope.hex;
      scope.rgba = drgba;
      myEfficientFn();
    }

    function changeColor(e) {
      if (bCanPreview && cdown) {
        canvas.style.cursor = "none";
        // get coordinates of current position
        var canvasOffset = angular.element(canvas).offset();
        var canvasX = Math.floor(e.pageX - canvasOffset.left);
        var canvasY = Math.floor(e.pageY - canvasOffset.top);
        angular.element(indicatorEl).css({
          left: canvasX + "px",
          top: canvasY + "px"
        });
        // get current pixel
        var imageData = ctx.getImageData(canvasX, canvasY, 1, 1);
        var pixel = imageData.data;
        colorUpdate(pixel[0], pixel[1], pixel[2]);
      }
    }

    function debounce(func, wait, immediate) {
      var timeout;
      return function() {
        var context = this,
          args = arguments;
        var later = function() {
          timeout = null;
          if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
      };
    }

    var myEfficientFn = debounce(function() {
      scope.value = scope.rgba;
      ngModel.$setViewValue(scope.value);
      ngModel.$commitViewValue(true);
      ngModel.$render();
      scope.$apply();
    }, 250);

    //Show
    angular.element(previewEl).mousedown(function(e) {
      e.stopPropagation();
      var popup = angular.element(module);
      if (angular.element(module).hasClass("hidemodule")) {
        popup.removeClass("hidemodule");
        scope.rgbaStringToUpdate(scope.value);
      } else {
        //popup.addClass('hidemodule');
      }
    });
    //hide
    angular.element(document).mousedown(function(e) {
      var popup = angular.element(module);
      if (!angular.element(module).hasClass("hidemodule")) {
        //popup.addClass('hidemodule');
      }
    });

    var bCanPreview = true;
    angular
      .element(canvas)
      .mousemove(function(e) {
        changeColor(e);
      })
      .mousedown(function(e) {
        cdown = true;
        changeColor(e);
      });
    angular.element(canvas).mouseup(function(e) {
      cdown = false;
      canvas.style.cursor = "crosshair";
    });

    angular
      .element(brightnessEl)
      .mousemove(function(e) {
        changeBrightness(e);
      })
      .mousedown(function(e) {
        bdown = true;
        changeBrightness(e);
      });
    angular.element(brightnessEl).mouseup(function(e) {
      bdown = false;
      canvas.style.cursor = "crosshair";
    });

    angular
      .element(transparencyEl)
      .mousemove(function(e) {
        changeTransparency(e);
      })
      .mousedown(function(e) {
        tdown = true;
        changeTransparency(e);
      });
    angular.element(transparencyEl).mouseup(function(e) {
      tdown = false;
      canvas.style.cursor = "crosshair";
    });

    angular.element(module).mousedown(function(e) {
      e.stopPropagation();
    });

    angular
      .element(module)
      .mouseup(function(e) {
        tdown = false;
        cdown = false;
        bdown = false;
        canvas.style.cursor = "crosshair";
      })
      .mouseleave(function(e) {
        tdown = false;
        cdown = false;
        bdown = false;
        canvas.style.cursor = "crosshair";
      });

    ngModel.$render = function() {
      scope.value = ngModel.$modelValue;
    };

    setTimeout(function() {
      var rgba = scope.value;
      rgba = rgba
        .substring(rgba.indexOf("(") + 1, rgba.lastIndexOf(")"))
        .split(/,\s*/);
      colorUpdate(rgba[0], rgba[1], rgba[2], rgba[3]);
      setTransparency(rgba[3]);
    }, 300);
    drawBg();
  }

  return {
    require: "?ngModel",
    scope: {
      value: "=ngModel"
    },
    link: link,
    template:
      '<div class="cpick-preview" ng-model="value">' +
      '<div class="cpick-module">' + //class hidemodule
      '<div class="cpick">' +
      '<canvas id="color-canvas"></canvas>' +
      '<div class="darkness"></div>' +
      "</div>" +
      '<div class="cpick-indicator"></div>' +
      '<div class="cpick-brightness">' +
      '<div class="cpick-brightness-indicator"></div>' +
      "</div>" +
      '<div class="cpick-transparency">' +
      '<div class="cpick-transparency-indicator"></div>' +
      "</div>" +
      //'<div style="color:black">{{rgba}}</div>'+
      '<div class="cpick-grayscale">' +
      '<div class="cpick-square" ng-repeat="scale in grayscale" ng-style="{\'background-color\': scale}" ng-click="rgbaStringToUpdate(scale)"></div>' +
      "</div>" +
      '<div class="cpick-presets">' +
      '<div class="cpick-square" ng-repeat="preset in presets" ng-style="{\'background-color\': preset}" ng-click="rgbaStringToUpdate(preset)"></div>' +
      "</div>" +
      "</div>" +
      "</div>"
  };
});
