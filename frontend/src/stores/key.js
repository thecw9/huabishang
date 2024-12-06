import { defineStore } from "pinia";

export const useKeyStore = defineStore("key", {
  state: () => {
    return { key: 0 };
  },
  actions: {
    setKey(newKey) {
      this.key = newKey;
    },
  },
});
