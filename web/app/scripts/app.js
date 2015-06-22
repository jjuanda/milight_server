/*
Copyright (c) 2015 The Polymer Project Authors. All rights reserved.
This code may only be used under the BSD style license found at http://polymer.github.io/LICENSE.txt
The complete set of authors may be found at http://polymer.github.io/AUTHORS.txt
The complete set of contributors may be found at http://polymer.github.io/CONTRIBUTORS.txt
Code distributed by Google as part of the polymer project is also
subject to an additional IP rights grant found at http://polymer.github.io/PATENTS.txt
*/

(function(document) {
  'use strict';

  // Grab a reference to our auto-binding template
  // and give it some initial binding values
  // Learn more about auto-binding templates at http://goo.gl/Dx1u2g
  var app = document.querySelector('#app');

  app.displayInstalledToast = function() {
    document.querySelector('#caching-complete').show();
  };

  // Listen for template bound event to know when bindings
  // have resolved and content has been stamped to the page
  app.addEventListener('dom-change', function() {
    console.log('Our app is ready to rock!');
  });

  // See https://github.com/Polymer/polymer/issues/1381
  window.addEventListener('WebComponentsReady', function() {
    // imports are loaded and elements have been registered
  });

  // Close drawer after menu item is selected if drawerPanel is narrow
  app.onMenuSelect = function() {
    var drawerPanel = document.querySelector('#paperDrawerPanel');
    if (drawerPanel.narrow) {
      drawerPanel.closeDrawer();
    }
  };

  app.initializeDefaultValue = function() {
    console.log('initialize Local Storage');
    this.value = {
      bridgeIP : '192.168.1.2'
    };
  };

  app.handleResponse = function(req) {
    console.log(req);
  };

  app.updateOptions = function() {
    this.$.api.updateOptions();
  };

  app.updateLights = function() {
    console.log('updateLights: ' + this.lightsOn);
    this.lightsBrightness = 0;
    this.$.api.setAllLights(this.lightsOn);
  };

  app.updateBrightness = function() {
    console.log('updateBrightness: ' + this.lightsBrightness);
    if (this.lightsBrightness == 0) {
      this.lightsOn = false;
    } else {
      this.lightsOn = true;
      this.$.api.setAllBrightness(this.lightsBrightness);
    }
  };

  app.updateColor = function(event) {
    console.log('updateColor: ' + event.detail.hex);
    this.$.api.setAllColor(event.detail.hex.substr(1));
  };

  app.updateHue = function(hue) {
    console.log('updateHue: ' + this.lightsHue);
    this.$.api.setAllHue(this.lightsHue);
  };
})(document);
