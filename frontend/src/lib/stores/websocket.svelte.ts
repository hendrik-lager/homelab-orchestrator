let socket: WebSocket | null = null;
let connected = $state(false);

export const wsStore = {
  get connected() { return connected; },

  connect() {
    const url = `ws://${window.location.host}/api/v1/ws`;
    socket = new WebSocket(url);
    socket.onopen = () => { connected = true; };
    socket.onclose = () => {
      connected = false;
      setTimeout(() => wsStore.connect(), 5000);
    };
    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type !== 'ping') console.log('WS:', msg);
    };
  },
};
