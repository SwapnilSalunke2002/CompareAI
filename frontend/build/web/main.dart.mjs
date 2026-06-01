// Compiles a dart2wasm-generated main module from `source` which can then
// instantiatable via the `instantiate` method.
//
// `source` needs to be a `Response` object (or promise thereof) e.g. created
// via the `fetch()` JS API.
export async function compileStreaming(source) {
  const builtins = {builtins: ['js-string']};
  return new CompiledApp(
      await WebAssembly.compileStreaming(source, builtins), builtins);
}

// Compiles a dart2wasm-generated wasm modules from `bytes` which is then
// instantiatable via the `instantiate` method.
export async function compile(bytes) {
  const builtins = {builtins: ['js-string']};
  return new CompiledApp(await WebAssembly.compile(bytes, builtins), builtins);
}

// DEPRECATED: Please use `compile` or `compileStreaming` to get a compiled app,
// use `instantiate` method to get an instantiated app and then call
// `invokeMain` to invoke the main function.
export async function instantiate(modulePromise, importObjectPromise) {
  var moduleOrCompiledApp = await modulePromise;
  if (!(moduleOrCompiledApp instanceof CompiledApp)) {
    moduleOrCompiledApp = new CompiledApp(moduleOrCompiledApp);
  }
  const instantiatedApp = await moduleOrCompiledApp.instantiate(await importObjectPromise);
  return instantiatedApp.instantiatedModule;
}

// DEPRECATED: Please use `compile` or `compileStreaming` to get a compiled app,
// use `instantiate` method to get an instantiated app and then call
// `invokeMain` to invoke the main function.
export const invoke = (moduleInstance, ...args) => {
  moduleInstance.exports.$invokeMain(args);
}

class CompiledApp {
  constructor(module, builtins) {
    this.module = module;
    this.builtins = builtins;
  }

  // The second argument is an options object containing:
  // `loadDeferredModules` is a JS function that takes an array of module names
  //   matching wasm files produced by the dart2wasm compiler. It also takes a
  //   callback that should be invoked for each loaded module with 2 arugments:
  //   (1) the module name, (2) the loaded module in a format supported by
  //   `WebAssembly.compile` or `WebAssembly.compileStreaming`. The callback
  //   returns a Promise that resolves when the module is instantiated.
  //   loadDeferredModules should return a Promise that resolves when all the
  //   modules have been loaded and the callback promises have resolved.
  // `loadDeferredId` is a JS function that takes load ID produced by the
  //   compiler when the `use-load-ids` option is passed. Each load ID maps to
  //   one or more wasm files as specified in the emitted JSON file. It also
  //   takes a callback that should be invoked for each loaded module with 2
  //   arugments: (1) the module name, (2) the loaded module in a format
  //   supported by `WebAssembly.compile` or `WebAssembly.compileStreaming`.
  //   The callback returns a Promise that resolves when the module is
  //   instantiated.
  //   loadDeferredModules should return a Promise that resolves when all the
  //   modules have been loaded and the callback promises have resolved.
  async instantiate(additionalImports, {loadDeferredModules, loadDeferredId} = {}) {
    let dartInstance;

    // Prints to the console
    function printToConsole(value) {
      if (typeof dartPrint == "function") {
        dartPrint(value);
        return;
      }
      if (typeof console == "object" && typeof console.log != "undefined") {
        console.log(value);
        return;
      }
      if (typeof print == "function") {
        print(value);
        return;
      }

      throw "Unable to print message: " + value;
    }

    // A special symbol attached to functions that wrap Dart functions.
    const jsWrappedDartFunctionSymbol = Symbol("JSWrappedDartFunction");

    function finalizeWrapper(dartFunction, wrapped) {
      wrapped.dartFunction = dartFunction;
      wrapped[jsWrappedDartFunctionSymbol] = true;
      return wrapped;
    }

    // Imports
    const dart2wasm = {
            AB: Function.prototype.call.bind(DataView.prototype.getInt32),
      AC: Function.prototype.call.bind(DataView.prototype.setUint16),
      AD: (string, times) => string.repeat(times),
      AE: (x0,x1) => x0[x1],
      AF: x0 => x0.x,
      AG: x0 => new Uint8Array(x0),
      AH: x0 => x0.selectionEnd,
      AI: x0 => x0.value,
      AJ: x0 => x0.selectedTrack,
      AK: (x0,x1) => { x0.max = x1 },
      B: () => new Error().stack,
      BB: Function.prototype.call.bind(DataView.prototype.getUint16),
      BC: Function.prototype.call.bind(DataView.prototype.setUint8),
      BD: o => {
        if (o === null || o === undefined) return 0;
        if (typeof(o) === 'string') return 1;
        return 2;
      },
      BE: x0 => x0.length,
      BF: x0 => x0.scrollTop,
      BG: (x0,x1,x2) => x0.set(x1,x2),
      BH: x0 => x0.value,
      BI: x0 => x0.done,
      BJ: x0 => x0.completed,
      BK: (x0,x1) => { x0.scrollLeft = x1 },
      C: (exn) => {
        let stackString = exn.toString();
        let frames = stackString.split('\n');
        let drop = 4;
        if (frames[0].startsWith('Error')) {
            drop += 1;
        }
        return frames.slice(drop).join('\n');
      },
      CB: Function.prototype.call.bind(DataView.prototype.getInt16),
      CC: Function.prototype.call.bind(DataView.prototype.setInt8),
      CD: x0 => x0.tabIndex,
      CE: (x0,x1) => x0.exec(x1),
      CF: x0 => x0.offsetTop,
      CG: x0 => x0.length,
      CH: x0 => x0.selectionDirection,
      CI: (o, m, a) => o[m].apply(o, a),
      CJ: x0 => x0.ready,
      CK: (x0,x1) => { x0.spellcheck = x1 },
      D: Function.prototype.call.bind(Number.prototype.toString),
      DB: Function.prototype.call.bind(DataView.prototype.getUint8),
      DC: o => {
        if (o === null || o === undefined) return 0;
        if (o instanceof Int8Array) return 1;
        return 2;
      },
      DD: (x0,x1) => x0.contains(x1),
      DE: x0 => x0.index,
      DF: x0 => x0.scrollLeft,
      DG: x0 => x0.buffer,
      DH: x0 => x0.selectionStart,
      DI: x0 => x0.iterator,
      DJ: x0 => x0.tracks,
      DK: (x0,x1) => { x0.disabled = x1 },
      E: Function.prototype.call.bind(BigInt.prototype.toString),
      EB: Function.prototype.call.bind(DataView.prototype.getInt8),
      EC: (o, start, length) => new Float64Array(o.buffer, o.byteOffset + start, length),
      ED: x0 => x0.activeElement,
      EE: x0 => x0.flags,
      EF: x0 => x0.offsetLeft,
      EG: x0 => x0.wasmMemory,
      EH: x0 => x0.selectionEnd,
      EI: () => globalThis.Symbol,
      EJ: x0 => x0.close(),
      EK: (x0,x1) => x0.transferFromImageBitmap(x1),
      F: Function.prototype.call.bind(Number.prototype.toString),
      FB: o => o.length,
      FC: (o, start, length) => new Float32Array(o.buffer, o.byteOffset + start, length),
      FD: x0 => x0.parentNode,
      FE: s => s.trim(),
      FF: x0 => x0.offsetParent,
      FG: () => globalThis.window._flutter_skwasmInstance,
      FH: (x0,x1) => x0.scrollIntoView(x1),
      FI: (x0,x1) => new Intl.Segmenter(x0,x1),
      FJ: (x0,x1) => ({frameIndex: x0,completeFramesOnly: x1}),
      FK: (x0,x1) => x0.getContext(x1),
      G: Function.prototype.call.bind(String.prototype.indexOf),
      GB: (o, i) => o[i],
      GC: (o, start, length) => new Uint32Array(o.buffer, o.byteOffset + start, length),
      GD: x0 => x0.tagName,
      GE: (a, s) => a.join(s),
      GF: x0 => x0.deltaMode,
      GG: x0 => x0.getReader(),
      GH: (x0,x1) => x0.replaceWith(x1),
      GI: x0 => x0.Segmenter,
      GJ: (x0,x1) => x0.decode(x1),
      GK: (x0,x1) => { x0.height = x1 },
      H: s => JSON.stringify(s),
      HB: o => {
        if (o === undefined) return 1;
        var type = typeof o;
        if (type === 'boolean') return 2;
        if (type === 'number') return 3;
        if (type === 'string') return 4;
        if (o instanceof Array) return 5;
        if (ArrayBuffer.isView(o)) {
          if (o instanceof Int8Array) return 6;
          if (o instanceof Uint8Array) return 7;
          if (o instanceof Uint8ClampedArray) return 8;
          if (o instanceof Int16Array) return 9;
          if (o instanceof Uint16Array) return 10;
          if (o instanceof Int32Array) return 11;
          if (o instanceof Uint32Array) return 12;
          if (o instanceof Float32Array) return 13;
          if (o instanceof Float64Array) return 14;
          if (o instanceof DataView) return 15;
        }
        if (o instanceof ArrayBuffer) return 16;
        // Feature check for `SharedArrayBuffer` before doing a type-check.
        if (globalThis.SharedArrayBuffer !== undefined &&
            o instanceof SharedArrayBuffer) {
            return 17;
        }
        if (o instanceof Promise) return 18;
        return 19;
      },
      HC: (o, start, length) => new Int32Array(o.buffer, o.byteOffset + start, length),
      HD: x0 => x0.target,
      HE: (x0,x1) => x0.error(x1),
      HF: x0 => x0.deltaY,
      HG: x0 => x0.value,
      HH: (x0,x1) => { x0.type = x1 },
      HI: () => new TextDecoder(),
      HJ: x0 => x0.displayHeight,
      HK: (x0,x1) => { x0.width = x1 },
      I: (s, p, i) => s.lastIndexOf(p, i),
      IB: (x0,x1) => x0.prepend(x1),
      IC: (o, start, length) => new Uint16Array(o.buffer, o.byteOffset + start, length),
      ID: x0 => x0.clientY,
      IE: () => globalThis.console,
      IF: x0 => x0.deltaX,
      IG: x0 => x0.done,
      IH: (x0,x1) => { x0.className = x1 },
      II: (a, i) => a.splice(i, 1),
      IJ: x0 => x0.displayWidth,
      IK: x0 => x0.height,
      J: o => o,
      JB: (x0,x1,x2,x3) => x0.addEventListener(x1,x2,x3),
      JC: (o, start, length) => new Int16Array(o.buffer, o.byteOffset + start, length),
      JD: x0 => x0.clientX,
      JE: s => s.trimRight(),
      JF: x0 => x0.wheelDeltaY,
      JG: x0 => x0.read(),
      JH: (x0,x1) => { x0.tabIndex = x1 },
      JI: a => a.pop(),
      JJ: x0 => x0.duration,
      JK: x0 => x0.width,
      K: o => String(o),
      KB: b => !!b,
      KC: (o, start, length) => new Uint8ClampedArray(o.buffer, o.byteOffset + start, length),
      KD: (x0,x1,x2) => x0.setAttribute(x1,x2),
      KE: x0 => x0.visibilityState,
      KF: x0 => x0.wheelDeltaX,
      KG: x0 => x0.body,
      KH: (x0,x1) => { x0.name = x1 },
      KI: (map, o, v) => map.set(o, v),
      KJ: x0 => x0.image,
      KK: x0 => x0.rasterEndMilliseconds,
      L: (c) =>
      queueMicrotask(() => dartInstance.exports.$invokeCallback(c)),
      LB: (module,f) => finalizeWrapper(f, function(x0) { return module.exports.K(f,arguments.length,x0) }),
      LC: (o, start, length) => new Uint8Array(o.buffer, o.byteOffset + start, length),
      LD: x0 => x0.getBoundingClientRect(),
      LE: (x0,x1,x2) => x0.removeEventListener(x1,x2),
      LF: x0 => x0.pressure,
      LG: x0 => x0.status,
      LH: (x0,x1) => { x0.placeholder = x1 },
      LI: (handle) => clearInterval(handle),
      LJ: () => globalThis.window.ImageDecoder,
      LK: x0 => x0.rasterStartMilliseconds,
      M: s => printToConsole(s),
      MB: (x0,x1) => x0.focus(x1),
      MC: (o, start, length) => new Int8Array(o.buffer, o.byteOffset + start, length),
      MD: (ms, c) =>
      setTimeout(() => dartInstance.exports.$invokeCallback(c),ms),
      ME: x0 => x0.disconnect(),
      MF: x0 => x0.tiltY,
      MG: x0 => x0.content,
      MH: (x0,x1) => { x0.autocomplete = x1 },
      MI: (ms, c) =>
      setInterval(() => dartInstance.exports.$invokeCallback(c), ms),
      MJ: x0 => x0.naturalHeight,
      MK: x0 => x0.imageBitmaps,
      N: (exn) => {
        if (exn instanceof Error) {
          return exn.stack;
        } else {
          return null;
        }
      },
      NB: () => ({}),
      NC: (x0,x1) => x0.querySelector(x1),
      ND: x0 => x0.bottom,
      NE: x0 => new Intl.Locale(x0),
      NF: x0 => x0.tiltX,
      NG: x0 => x0.document,
      NH: (x0,x1) => { x0.name = x1 },
      NI: () => Date.now(),
      NJ: x0 => x0.naturalWidth,
      NK: x0 => x0.canvasKitMaximumSurfaces,
      O: o => o === undefined,
      OB: (o, p, v) => o[p] = v,
      OC: (x0,x1) => x0.item(x1),
      OD: x0 => x0.top,
      OE: x0 => x0.region,
      OF: x0 => x0.pointerType,
      OG: (x0,x1) => x0.fetch(x1),
      OH: (x0,x1) => { x0.placeholder = x1 },
      OI: x0 => x0.debugSkipFontRetryDelay,
      OJ: (x0,x1) => x0.createElement(x1),
      OK: x0 => x0.nextSibling,
      P: (l, r) => l === r,
      PB: () => [],
      PC: x0 => x0.length,
      PD: x0 => x0.right,
      PE: x0 => x0.script,
      PF: x0 => x0.pointerId,
      PG: x0 => x0.assetBase,
      PH: (x0,x1) => { x0.action = x1 },
      PI: () => new AbortController(),
      PJ: (x0,x1) => { x0.pointerEvents = x1 },
      PK: (x0,x1) => x0.debug(x1),
      Q: x0 => x0.random(),
      QB: (a, i) => a.push(i),
      QC: (x0,x1) => x0.querySelectorAll(x1),
      QD: x0 => x0.left,
      QE: x0 => x0.language,
      QF: x0 => x0.getCoalescedEvents(),
      QG: (x0,x1) => new OffscreenCanvas(x0,x1),
      QH: (x0,x1) => { x0.method = x1 },
      QI: (x0,x1,x2,x3,x4,x5) => ({method: x0,headers: x1,body: x2,credentials: x3,redirect: x4,signal: x5}),
      QJ: (x0,x1) => { x0.height = x1 },
      R: o => o,
      RB: x0 => new Int8Array(x0),
      RC: (x0,x1) => x0.getAttribute(x1),
      RD: x0 => x0.clientY,
      RE: x0 => x0.languages,
      RF: x0 => x0.blur(),
      RG: Function.prototype.call.bind(DataView.prototype.getBigInt64),
      RH: (x0,x1) => { x0.noValidate = x1 },
      RI: (x0,x1) => globalThis.fetch(x0,x1),
      RJ: (x0,x1) => { x0.width = x1 },
      S: o => {
        if (o === undefined || o === null) return 0;
        if (typeof o === 'number') return 1;
        return 2;
      },
      SB: (jsArray, jsArrayOffset, wasmArray, wasmArrayOffset, length) => {
        const getValue = dartInstance.exports.$wasmI8ArrayGet;
        for (let i = 0; i < length; i++) {
          jsArray[jsArrayOffset + i] = getValue(wasmArray, wasmArrayOffset + i);
        }
      },
      SC: (x0,x1) => x0.appendChild(x1),
      SD: x0 => x0.clientX,
      SE: (x0,x1) => x0.observe(x1),
      SF: x0 => x0.button,
      SG: Function.prototype.call.bind(DataView.prototype.setBigInt64),
      SH: (x0,x1) => x0.removeAttribute(x1),
      SI: (x0,x1) => x0.get(x1),
      SJ: x0 => x0.style,
      T: () => globalThis.Math,
      TB: x0 => new Uint8Array(x0),
      TC: (x0,x1) => x0.append(x1),
      TD: x0 => x0.changedTouches,
      TE: (module,f) => finalizeWrapper(f, function(x0,x1) { return module.exports.L(f,arguments.length,x0,x1) }),
      TF: x0 => x0.innerHeight,
      TG: (o, start, length) => new BigInt64Array(o.buffer, o.byteOffset + start, length),
      TH: x0 => x0.isConnected,
      TI: (module,f) => finalizeWrapper(f, function(x0,x1,x2) { return module.exports.Q(f,arguments.length,x0,x1,x2) }),
      TJ: (x0,x1) => { x0.src = x1 },
      U: (x0,x1) => x0.didCreateEngineInitializer(x1),
      UB: x0 => new Uint8ClampedArray(x0),
      UC: (x0,x1,x2,x3) => x0.setProperty(x1,x2,x3),
      UD: x0 => x0.offsetY,
      UE: x0 => new ResizeObserver(x0),
      UF: x0 => x0.innerWidth,
      UG: (x0,x1,x2,x3) => x0.pushState(x1,x2,x3),
      UH: x0 => x0.click(),
      UI: (x0,x1) => x0.forEach(x1),
      UJ: () => globalThis.document,
      V: (module,f) => finalizeWrapper(f, function(x0) { return module.exports.C(f,arguments.length,x0) }),
      VB: x0 => new Int16Array(x0),
      VC: x0 => x0.style,
      VD: x0 => x0.offsetX,
      VE: x0 => x0.computedStyleMap(),
      VF: x0 => x0.height,
      VG: x0 => x0.history,
      VH: (x0,x1) => x0.getElementsByClassName(x1),
      VI: x0 => x0.name,
      VJ: x0 => x0.src,
      W: (module,f) => finalizeWrapper(f, function() { return module.exports.D(f,arguments.length) }),
      WB: x0 => new Uint16Array(x0),
      WC: x0 => x0.debugShowSemanticsNodes,
      WD: x0 => x0.type,
      WE: (x0,x1) => x0.get(x1),
      WF: x0 => x0.width,
      WG: x0 => x0.search,
      WH: (jsArray, jsArrayOffset, wasmArray, wasmArrayOffset, length) => {
        const setValue = dartInstance.exports.$wasmF32ArraySet;
        for (let i = 0; i < length; i++) {
          setValue(wasmArray, wasmArrayOffset + i, jsArray[jsArrayOffset + i]);
        }
      },
      WI: x0 => x0.statusText,
      WJ: x0 => x0.decode(),
      X: (x0,x1) => ({initializeEngine: x0,autoStart: x1}),
      XB: x0 => new Int32Array(x0),
      XC: o => {
        if (o === undefined || o === null) return 0;
        if (typeof o === 'boolean') return 1;
        return 2;
      },
      XD: (handle) => clearTimeout(handle),
      XE: (x0,x1) => x0.getPropertyValue(x1),
      XF: x0 => x0.clientHeight,
      XG: x0 => x0.location,
      XH: (jsArray, jsArrayOffset, wasmArray, wasmArrayOffset, length) => {
        const setValue = dartInstance.exports.$wasmF64ArraySet;
        for (let i = 0; i < length; i++) {
          setValue(wasmArray, wasmArrayOffset + i, jsArray[jsArrayOffset + i]);
        }
      },
      XI: x0 => x0.url,
      XJ: (x0,x1,x2,x3) => x0.open(x1,x2,x3),
      Y: (module,f) => finalizeWrapper(f, function(x0,x1) { return module.exports.E(f,arguments.length,x0,x1) }),
      YB: (jsArray, jsArrayOffset, wasmArray, wasmArrayOffset, length) => {
        const getValue = dartInstance.exports.$wasmI32ArrayGet;
        for (let i = 0; i < length; i++) {
          jsArray[jsArrayOffset + i] = getValue(wasmArray, wasmArrayOffset + i);
        }
      },
      YC: (x0,x1) => x0.warn(x1),
      YD: (x0,x1) => x0.closest(x1),
      YE: x0 => globalThis.parseFloat(x0),
      YF: x0 => x0.clientWidth,
      YG: x0 => x0.pathname,
      YH: (x0,x1) => x0.dispatchEvent(x1),
      YI: x0 => x0.status,
      YJ: (module,f) => finalizeWrapper(f, function(x0) { return module.exports.R(f,arguments.length,x0) }),
      Z: x0 => new Promise(x0),
      ZB: x0 => new Uint32Array(x0),
      ZC: x0 => x0.console,
      ZD: x0 => x0.maxTouchPoints,
      ZE: (x0,x1) => x0.getComputedStyle(x1),
      ZF: (x0,x1) => { x0.content = x1 },
      ZG: (x0,x1,x2,x3) => x0.replaceState(x1,x2,x3),
      ZH: (x0,x1) => x0.createEvent(x1),
      ZI: x0 => x0.cancel(),
      ZJ: (x0,x1,x2) => x0.addEventListener(x1,x2),
      a: (x0,x1,x2) => x0.call(x1,x2),
      aB: x0 => new Float32Array(x0),
      aC: () => globalThis.window,
      aD: x0 => x0.platform,
      aE: (o, p) => p in o,
      aF: (x0,x1) => { x0.name = x1 },
      aG: x0 => x0.state,
      aH: (x0,x1,x2,x3) => x0.initEvent(x1,x2,x3),
      aI: x0 => x0.getReader(),
      aJ: (module,f) => finalizeWrapper(f, function(x0) { return module.exports.S(f,arguments.length,x0) }),
      b: (constructor, args) => {
        const factoryFunction = constructor.bind.apply(
            constructor, [null, ...args]);
        return new factoryFunction();
      },
      bB: (jsArray, jsArrayOffset, wasmArray, wasmArrayOffset, length) => {
        const getValue = dartInstance.exports.$wasmF32ArrayGet;
        for (let i = 0; i < length; i++) {
          jsArray[jsArrayOffset + i] = getValue(wasmArray, wasmArrayOffset + i);
        }
      },
      bC: (o, c) => o instanceof c,
      bD: s => new Date(s * 1000).getTimezoneOffset() * 60,
      bE: (x0,x1) => { x0.textContent = x1 },
      bF: x0 => x0.head,
      bG: x0 => x0.hash,
      bH: x0 => x0.readText(),
      bI: x0 => x0.read(),
      bJ: x0 => x0.send(),
      c: x0 => new Array(x0),
      cB: x0 => new Float64Array(x0),
      cC: (string, token) => string.split(token),
      cD: Date.now,
      cE: x0 => x0.documentElement,
      cF: (x0,x1) => x0.removeChild(x1),
      cG: (x0,x1) => x0.go(x1),
      cH: x0 => x0.clipboard,
      cI: x0 => x0.value,
      cJ: x0 => x0.status,
      d: o => [o],
      dB: (jsArray, jsArrayOffset, wasmArray, wasmArrayOffset, length) => {
        const getValue = dartInstance.exports.$wasmF64ArrayGet;
        for (let i = 0; i < length; i++) {
          jsArray[jsArrayOffset + i] = getValue(wasmArray, wasmArrayOffset + i);
        }
      },
      dC: o => o instanceof Array,
      dD: x0 => x0.body,
      dE: (module,f) => finalizeWrapper(f, function(x0) { return module.exports.M(f,arguments.length,x0) }),
      dF: x0 => x0.firstChild,
      dG: x0 => x0.parentElement,
      dH: (x0,x1) => x0.writeText(x1),
      dI: x0 => x0.done,
      dJ: x0 => x0.response,
      e: (o0, o1) => [o0, o1],
      eB: x0 => new ArrayBuffer(x0),
      eC: (a, i) => a[i],
      eD: () => globalThis.document,
      eE: x0 => x0.matches,
      eF: x0 => x0.viewConstraints,
      eG: (x0,x1) => x0.querySelectorAll(x1),
      eH: x0 => x0.unlock(),
      eI: x0 => x0.body,
      eJ: (x0,x1) => { x0.responseType = x1 },
      f: (o0, o1, o2) => [o0, o1, o2],
      fB: (x0,x1,x2) => new Uint8Array(x0,x1,x2),
      fC: a => a.length,
      fD: (x0,x1,x2) => x0.addEventListener(x1,x2),
      fE: (x0,x1) => x0.matchMedia(x1),
      fF: x0 => x0.hostElement,
      fG: (x0,x1) => x0.requestAnimationFrame(x1),
      fH: (x0,x1) => x0.lock(x1),
      fI: x0 => x0.headers,
      fJ: () => new XMLHttpRequest(),
      g: (o0, o1, o2, o3) => [o0, o1, o2, o3],
      gB: (x0,x1,x2) => new DataView(x0,x1,x2),
      gC: (x0,x1) => x0.test(x1),
      gD: x0 => x0.hasFocus(),
      gE: x0 => x0.matches,
      gF: x0 => x0.loader,
      gG: (module,f) => finalizeWrapper(f, function(x0) { return module.exports.P(f,arguments.length,x0) }),
      gH: x0 => x0.orientation,
      gI: x0 => x0.signal,
      gJ: (x0,x1,x2) => x0.setRequestHeader(x1,x2),
      h: (x0,x1,x2) => { x0[x1] = x2 },
      hB: (o, p) => o[p],
      hC: x0 => x0.userAgent,
      hD: x0 => x0.relatedTarget,
      hE: x0 => x0.language,
      hF: () => globalThis._flutter,
      hG: x0 => x0.now(),
      hH: (x0,x1) => { x0.title = x1 },
      hI: () => {
        return typeof process != "undefined" &&
               Object.prototype.toString.call(process) == "[object process]" &&
               process.platform == "win32"
      },
      hJ: x0 => x0.input,
      i: (o, p) => o[p],
      iB: (b, o) => new DataView(b, o),
      iC: x0 => x0.navigator,
      iD: x0 => x0.shiftKey,
      iE: (x0,x1,x2,x3) => x0.register(x1,x2,x3),
      iF: o => {
        const proto = Object.getPrototypeOf(o);
        return proto === Object.prototype || proto === null;
      },
      iG: x0 => x0.performance,
      iH: (x0,x1) => x0.vibrate(x1),
      iI: () => {
        // On browsers return `globalThis.location.href`
        if (globalThis.location != null) {
          return globalThis.location.href;
        }
        return null;
      },
      iJ: (o, p) => p in o,
      j: () => globalThis,
      jB: (b, o, l) => new DataView(b, o, l),
      jC: Function.prototype.call.bind(String.prototype.toLowerCase),
      jD: s => s.trimLeft(),
      jE: () => globalThis.window.FinalizationRegistry,
      jF: o => Object.keys(o),
      jG: (d, digits) => d.toFixed(digits),
      jH: x0 => x0.arrayBuffer(),
      jI: x0 => x0.pop(),
      jJ: x0 => x0.groups,
      k: (module,f) => finalizeWrapper(f, function(x0) { return module.exports.F(f,arguments.length,x0) }),
      kB: o => o.buffer,
      kC: Object.is,
      kD: (a, i, v) => a[i] = v,
      kE: (module,f) => finalizeWrapper(f, function(x0) { return module.exports.N(f,arguments.length,x0) }),
      kF: x0 => x0.state,
      kG: x0 => x0.maxHeight,
      kH: o => {
        if (o === null || o === undefined) return 0;
        if (o instanceof ArrayBuffer) return 1;
        if (globalThis.SharedArrayBuffer !== undefined &&
            o instanceof SharedArrayBuffer) {
          return 2;
        }
        return 3;
      },
      kI: (x0,x1) => x0.revokeObjectURL(x1),
      kJ: () => globalThis.window.navigator.userAgent,
      l: x0 => ({runApp: x0}),
      lB: o => o.byteOffset,
      lC: x0 => x0.vendor,
      lD: (decoder, codeUnits) => decoder.decode(codeUnits),
      lE: x0 => new window.FinalizationRegistry(x0),
      lF: x0 => x0.hostElement,
      lG: x0 => x0.maxWidth,
      lH: () => typeof dartUseDateNowForTicks !== "undefined",
      lI: (x0,x1,x2,x3,x4) => globalThis.createImageBitmap(x0,x1,x2,x3,x4),
      lJ: (map, o) => map.get(o),
      m: (module,f) => finalizeWrapper(f, function(x0) { return module.exports.G(f,arguments.length,x0) }),
      mB: o => {
        if (o === null || o === undefined) return 0;
        if (o instanceof Float64Array) return 1;
        return 2;
      },
      mC: (x0,x1) => x0.createTextNode(x1),
      mD: () => new TextDecoder("utf-8", {fatal: true}),
      mE: (x0,x1) => x0.unregister(x1),
      mF: x0 => x0.multiViewEnabled,
      mG: x0 => x0.minHeight,
      mH: () => Date.now(),
      mI: x0 => x0.naturalHeight,
      mJ: () => new WeakMap(),
      n: (module,f) => finalizeWrapper(f, function(x0) { return module.exports.H(f,arguments.length,x0) }),
      nB: Function.prototype.call.bind(DataView.prototype.setFloat64),
      nC: (x0,x1) => { x0.id = x1 },
      nD: () => new TextDecoder("utf-8", {fatal: false}),
      nE: (x0,x1) => x0.contains(x1),
      nF: (x0,x1) => x0.querySelector(x1),
      nG: x0 => x0.minWidth,
      nH: () => 1000 * performance.now(),
      nI: x0 => x0.naturalWidth,
      nJ: x0 => new WeakRef(x0),
      o: (x0,x1) => ({addView: x0,removeView: x1}),
      oB: Function.prototype.call.bind(DataView.prototype.setFloat32),
      oC: (x0,x1) => { x0.nonce = x1 },
      oD: s => s.toUpperCase(),
      oE: (s) => +s,
      oF: (module,f) => finalizeWrapper(f, function(x0) { return module.exports.O(f,arguments.length,x0) }),
      oG: (x0,x1) => x0.removeProperty(x1),
      oH: (x0,x1,x2) => x0.slice(x1,x2),
      oI: x0 => x0.decode(),
      oJ: x0 => x0.deref(),
      p: o => o,
      pB: (t, s) => t.set(s),
      pC: x0 => x0.nonce,
      pD: (jsArray, jsArrayOffset, wasmArray, wasmArrayOffset, length) => {
        const setValue = dartInstance.exports.$wasmI8ArraySet;
        for (let i = 0; i < length; i++) {
          setValue(wasmArray, wasmArrayOffset + i, jsArray[jsArrayOffset + i]);
        }
      },
      pE: s => {
        if (!/^\s*[+-]?(?:Infinity|NaN|(?:\.\d+|\d+(?:\.\d*)?)(?:[eE][+-]?\d+)?)\s*$/.test(s)) {
          return NaN;
        }
        return parseFloat(s);
      },
      pF: x0 => x0.keyCode,
      pG: (x0,x1) => x0.add(x1),
      pH: (x0,x1) => x0.decode(x1),
      pI: (x0,x1) => { x0.src = x1 },
      pJ: () => globalThis.WeakRef,
      q: o => typeof o === 'function' && o[jsWrappedDartFunctionSymbol] === true,
      qB: o => {
        if (o === null || o === undefined) return 0;
        if (o instanceof Float32Array) return 1;
        return 2;
      },
      qC: () => globalThis.window.flutterConfiguration,
      qD: (jsArray, jsArrayOffset, wasmArray, wasmArrayOffset, length) => {
        const setValue = dartInstance.exports.$wasmI32ArraySet;
        for (let i = 0; i < length; i++) {
          setValue(wasmArray, wasmArrayOffset + i, jsArray[jsArrayOffset + i]);
        }
      },
      qE: x0 => x0.classList,
      qF: x0 => x0.location,
      qG: x0 => x0.data,
      qH: (x0,x1) => x0.adoptText(x1),
      qI: (x0,x1) => { x0.decoding = x1 },
      qJ: (o, offsetInBytes, lengthInBytes) => {
        var dst = new ArrayBuffer(lengthInBytes);
        new Uint8Array(dst).set(new Uint8Array(o, offsetInBytes, lengthInBytes));
        return new DataView(dst);
      },
      r: f => f.dartFunction,
      rB: o => {
        if (o === null || o === undefined) return 0;
        if (o instanceof Uint32Array) return 1;
        return 2;
      },
      rC: (x0,x1) => x0.attachShadow(x1),
      rD: (o, p, r) => o.replace(p, () => r),
      rE: x0 => x0.key,
      rF: (x0,x1) => x0.getModifierState(x1),
      rG: (x0,x1) => { x0.scrollTop = x1 },
      rH: x0 => x0.first(),
      rI: (x0,x1) => { x0.crossOrigin = x1 },
      rJ: (a, s, e) => a.slice(s, e),
      s: (module,f) => finalizeWrapper(f, function(x0) { return module.exports.I(f,arguments.length,x0) }),
      sB: o => {
        if (o === null || o === undefined) return 0;
        if (o instanceof Int32Array) return 1;
        return 2;
      },
      sC: (x0,x1) => x0.createElement(x1),
      sD: (x0,x1) => { x0.lastIndex = x1 },
      sE: (x0,x1) => x0.getModifierState(x1),
      sF: x0 => x0.metaKey,
      sG: (x0,x1,x2) => x0.setSelectionRange(x1,x2),
      sH: x0 => x0.next(),
      sI: (x0,x1) => x0.createObjectURL(x1),
      sJ: x0 => x0.abort(),
      t: (module,f) => finalizeWrapper(f, function(x0,x1) { return module.exports.J(f,arguments.length,x0,x1) }),
      tB: o => o instanceof Uint16Array,
      tC: x0 => x0.scale,
      tD: (s, m) => {
        try {
          return new RegExp(s, m);
        } catch (e) {
          return String(e);
        }
      },
      tE: x0 => x0.timeStamp,
      tF: x0 => x0.altKey,
      tG: (x0,x1) => { x0.value = x1 },
      tH: x0 => x0.current(),
      tI: x0 => x0.URL,
      tJ: (x0,x1,x2) => x0.insertBefore(x1,x2),
      u: (p, s, f) => p.then(s, (e) => f(e, e === undefined)),
      uB: o => o instanceof Int16Array,
      uC: x0 => x0.visualViewport,
      uD: o => o instanceof RegExp,
      uE: x0 => x0.preventDefault(),
      uF: x0 => x0.ctrlKey,
      uG: (x0,x1,x2) => x0.setSelectionRange(x1,x2),
      uH: (x0,x1) => new Intl.v8BreakIterator(x0,x1),
      uI: x0 => new Blob(x0),
      uJ: x0 => x0.id,
      v: Function.prototype.call.bind(Object.getOwnPropertyDescriptor(DataView.prototype, 'byteLength').get),
      vB: o => o instanceof Uint8ClampedArray,
      vC: x0 => x0.devicePixelRatio,
      vD: x0 => x0.dotAll,
      vE: x0 => x0.parent,
      vF: x0 => x0.isComposing,
      vG: (x0,x1) => { x0.value = x1 },
      vH: x0 => x0.v8BreakIterator,
      vI: (x0,x1,x2,x3,x4) => ({type: x0,data: x1,premultiplyAlpha: x2,colorSpaceConversion: x3,preferAnimation: x4}),
      vJ: x0 => x0.offsetHeight,
      w: (o) => new DataView(o.buffer, o.byteOffset, o.byteLength),
      wB: o => {
        if (o === null || o === undefined) return 0;
        if (o instanceof Uint8Array) return 1;
        return 2;
      },
      wC: x0 => x0.height,
      wD: x0 => x0.unicode,
      wE: (x0,x1) => x0.hasAttribute(x1),
      wF: x0 => x0.code,
      wG: s => {
        if (/[[\]{}()*+?.\\^$|]/.test(s)) {
            s = s.replace(/[[\]{}()*+?.\\^$|]/g, '\\$&');
        }
        return s;
      },
      wH: () => globalThis.Intl,
      wI: x0 => new window.ImageDecoder(x0),
      wJ: x0 => x0.offsetWidth,
      x: Function.prototype.call.bind(DataView.prototype.getFloat64),
      xB: Function.prototype.call.bind(DataView.prototype.setInt32),
      xC: x0 => x0.width,
      xD: x0 => x0.ignoreCase,
      xE: x0 => x0.buttons,
      xF: x0 => x0.stopPropagation(),
      xG: x0 => x0.value,
      xH: (x0,x1) => x0.segment(x1),
      xI: x0 => x0.name,
      xJ: (x0,x1) => { x0.disabled = x1 },
      y: Function.prototype.call.bind(DataView.prototype.getFloat32),
      yB: Function.prototype.call.bind(DataView.prototype.setUint32),
      yC: x0 => x0.screen,
      yD: x0 => x0.multiline,
      yE: x0 => x0.ctrlKey,
      yF: x0 => x0.repeat,
      yG: x0 => x0.selectionDirection,
      yH: x0 => x0.index,
      yI: x0 => x0.repetitionCount,
      yJ: x0 => x0.disabled,
      z: Function.prototype.call.bind(DataView.prototype.getUint32),
      zB: Function.prototype.call.bind(DataView.prototype.setInt16),
      zC: x0 => x0.remove(),
      zD: (o, p, r) => o.replaceAll(p, () => r),
      zE: x0 => x0.y,
      zF: x0 => x0.fontFallbackBaseUrl,
      zG: x0 => x0.selectionStart,
      zH: x0 => x0.next(),
      zI: x0 => x0.frameCount,
      zJ: (x0,x1) => { x0.min = x1 },

    };

    const baseImports = {
      _: dart2wasm,
      Math: Math,
      Date: Date,
      Object: Object,
      Array: Array,
      Reflect: Reflect,
      WebAssembly: {
        JSTag: WebAssembly.JSTag,
      },
      "": new Proxy({}, { get(_, prop) { return prop; } }),

    };

    const jsStringPolyfill = {
      "charCodeAt": (s, i) => s.charCodeAt(i),
      "compare": (s1, s2) => {
        if (s1 < s2) return -1;
        if (s1 > s2) return 1;
        return 0;
      },
      "concat": (s1, s2) => s1 + s2,
      "equals": (s1, s2) => s1 === s2,
      "fromCharCode": (i) => String.fromCharCode(i),
      "length": (s) => s.length,
      "substring": (s, a, b) => s.substring(a, b),
      "fromCharCodeArray": (a, start, end) => {
        if (end <= start) return '';

        const read = dartInstance.exports.$wasmI16ArrayGet;
        let result = '';
        let index = start;
        const chunkLength = Math.min(end - index, 500);
        let array = new Array(chunkLength);
        while (index < end) {
          const newChunkLength = Math.min(end - index, 500);
          for (let i = 0; i < newChunkLength; i++) {
            array[i] = read(a, index++);
          }
          if (newChunkLength < chunkLength) {
            array = array.slice(0, newChunkLength);
          }
          result += String.fromCharCode(...array);
        }
        return result;
      },
      "intoCharCodeArray": (s, a, start) => {
        if (s === '') return 0;

        const write = dartInstance.exports.$wasmI16ArraySet;
        for (var i = 0; i < s.length; ++i) {
          write(a, start++, s.charCodeAt(i));
        }
        return s.length;
      },
      "test": (s) => typeof s == "string",
    };


    

    dartInstance = await WebAssembly.instantiate(this.module, {
      ...baseImports,
      ...additionalImports,
      
      "wasm:js-string": jsStringPolyfill,
    });
    dartInstance.exports.B(dartInstance);

    return new InstantiatedApp(this, dartInstance);
  }
}

class InstantiatedApp {
  constructor(compiledApp, instantiatedModule) {
    this.compiledApp = compiledApp;
    this.instantiatedModule = instantiatedModule;
  }

  // Call the main function with the given arguments.
  invokeMain(...args) {
    this.instantiatedModule.exports.$invokeMain(args);
  }
}
