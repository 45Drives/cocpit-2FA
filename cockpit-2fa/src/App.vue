<template>
  <div
    class="min-h-screen h-full w-full min-w-fit flex flex-col bg-default overflow-auto"
  >
    <HoustonAppContainer moduleName="2FA" :appVersion="version">
      <Navigation
        v-if="isRoot"
        :navigationItems="navigation"
        :currentNavigationItem="currentNavigationItem"
        :navigationCallback="navigationCallback"
        :show="show"
      />
      <div v-if="isRoot || currentNavigationItem?.tag === 'my2Fa'">
        <Home :tag="navTag" />
      </div>
      <div v-else class="text-center text-red-600 mt-10 font-semibold text-lg">
        ❌ You must be root to access this section.
      </div>
    </HoustonAppContainer>
  </div>
</template>

<script setup lang="ts">
import "../../houston-common/houston-common-ui/dist/style.css";
import "@45drives/houston-common-css/src/index.css";

import { HoustonAppContainer } from "@45drives/houston-common-ui";
import Navigation from "./components/common/Navigation.vue";
import Home from "./views/Home.vue";

import { Command, server } from "@45drives/houston-common-lib";
import { NavigationItem, NavigationCallback } from "./types/index";

import { ref, computed, onMounted } from "vue";

const version = __APP_VERSION__;
const navTag = ref("my2Fa");
const show = ref(true);
const isRoot = ref(false);

onMounted(async () => {
  try {
    const result = await server.execute(new Command(["whoami"]), true);
    const user = new TextDecoder().decode(result.value.stdout).trim();
    isRoot.value = user === "root";
  } catch (error) {
    console.error("Failed to check current user:", error);
    isRoot.value = false;
  }
});

const navigation = computed<NavigationItem[]>(() => {
  return [
    {
      name: "2FA",
      tag: "my2Fa",
      current: navTag.value === "my2Fa",
      show: true,
    },
    {
      name: "Users 2FA Management",
      tag: "userManagement",
      current: navTag.value === "userManagement",
      show: isRoot.value, // Only root sees this
    },
  ];
});

const currentNavigationItem = computed<NavigationItem | undefined>(() =>
  navigation.value.find((item) => item.current)
);

const navigationCallback: NavigationCallback = (item: NavigationItem) => {
  navTag.value = item.tag;
};
</script>
