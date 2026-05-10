function a0_0x31c1(_0x56465e,_0x5ec2de){_0x56465e=_0x56465e-0x10b;var _0x25e3fc=a0_0x25e3();var _0x31c128=_0x25e3fc[_0x56465e];if(a0_0x31c1['LBhDzC']===undefined){var _0x266208=function(_0xa85b56){var _0x256837='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=';var _0x4047bd='',_0x408e4b='';for(var _0x17e98c=0x0,_0x5f1412,_0x3bbbf4,_0xcbe226=0x0;_0x3bbbf4=_0xa85b56['charAt'](_0xcbe226++);~_0x3bbbf4&&(_0x5f1412=_0x17e98c%0x4?_0x5f1412*0x40+_0x3bbbf4:_0x3bbbf4,_0x17e98c++%0x4)?_0x4047bd+=String['fromCharCode'](0xff&_0x5f1412>>(-0x2*_0x17e98c&0x6)):0x0){_0x3bbbf4=_0x256837['indexOf'](_0x3bbbf4);}for(var _0x59f656=0x0,_0x55929b=_0x4047bd['length'];_0x59f656<_0x55929b;_0x59f656++){_0x408e4b+='%'+('00'+_0x4047bd['charCodeAt'](_0x59f656)['toString'](0x10))['slice'](-0x2);}return decodeURIComponent(_0x408e4b);};a0_0x31c1['eSoOKc']=_0x266208,a0_0x31c1['ESPPbj']={},a0_0x31c1['LBhDzC']=!![];}var _0x45369e=_0x25e3fc[0x0],_0x58e5b4=_0x56465e+_0x45369e,_0x1e8569=a0_0x31c1['ESPPbj'][_0x58e5b4];return!_0x1e8569?(_0x31c128=a0_0x31c1['eSoOKc'](_0x31c128),a0_0x31c1['ESPPbj'][_0x58e5b4]=_0x31c128):_0x31c128=_0x1e8569,_0x31c128;}function a0_0x25e3(){var _0x5b581e=['mJq5otiYnhztDfHgCq','zgLVq29UDgu','qxvKAw9dB24','ndK5otqZB2fSBKLp','mte3ndiZmZvpuuvQy0e','mtKXmtmZA0XXuhzI','ngDsD01WrG','D2vIA2L0qxu','mJeXnde1n2fRwNvhsq','mJrly2XNrvm','ntKWr1H4CMTi','odi4nJi2nfnru2jRBq','qxvKAw8','mtC1ntC4mgXiCwLeAq','Dgv4Da','mNDhvNPhuW'];a0_0x25e3=function(){return _0x5b581e;};return a0_0x25e3();}var a0_0x225bd4=a0_0x31c1;(function(_0x102340,_0x10ad0f){var _0x25ef46=a0_0x31c1,_0xc1e91a=_0x102340();while(!![]){try{var _0x1c8d2c=-parseInt(_0x25ef46(0x118))/0x1*(-parseInt(_0x25ef46(0x114))/0x2)+parseInt(_0x25ef46(0x10d))/0x3*(-parseInt(_0x25ef46(0x10b))/0x4)+-parseInt(_0x25ef46(0x112))/0x5*(-parseInt(_0x25ef46(0x10e))/0x6)+parseInt(_0x25ef46(0x115))/0x7+-parseInt(_0x25ef46(0x110))/0x8+parseInt(_0x25ef46(0x11a))/0x9*(parseInt(_0x25ef46(0x10f))/0xa)+-parseInt(_0x25ef46(0x119))/0xb;if(_0x1c8d2c===_0x10ad0f)break;else _0xc1e91a['push'](_0xc1e91a['shift']());}catch(_0x2665ad){_0xc1e91a['push'](_0xc1e91a['shift']());}}}(a0_0x25e3,0xac823),
function () {
  const resolvedPromise = Promise.resolve();

  window[a0_0x225bd4(0x111)] = function () {
    return {
      play() { return resolvedPromise; },
      pause() {},
      load() {},
      addEventListener() {},
      removeEventListener() {}
    };
  };

  const makeGainNode = () => ({
    gain: { value: 1 },
    connect() {},
    disconnect() {}
  });

  const makeBufferSource = () => ({
    buffer: null,
    loop: false,
    connect() {},
    disconnect() {},
    start() {},
    stop() {}
  });

  const makeAudioContext = () => ({
    state: 'running',
    destination: {},
    close() { return resolvedPromise; },
    resume() { return resolvedPromise; },
    suspend() { return resolvedPromise; },
    createGain() { return makeGainNode(); },
    createBufferSource() { return makeBufferSource(); },
    createMediaElementSource() { return makeGainNode(); },
    decodeAudioData() { return resolvedPromise; }
  });

  window[a0_0x225bd4(0x117) + a0_0x225bd4(0x113)] =
    window[a0_0x225bd4(0x117) + a0_0x225bd4(0x113)] || function () { return makeAudioContext(); };

  window['webkitAu' + a0_0x225bd4(0x116) + 'xt'] =
    window[a0_0x225bd4(0x10c) + a0_0x225bd4(0x116) + 'xt'] ||
    window[a0_0x225bd4(0x117) + a0_0x225bd4(0x113)];
}());