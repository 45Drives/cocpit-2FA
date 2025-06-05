<template>
  <div class="bg-default">
    <div>
      <div class="border-b border-default">
        <nav class="-mb-px flex justify-center" aria-label="Tabs">
          <a
            v-for="item in props.navigationItems"
            :key="item.name"
            @click.prevent="navigationCallback(item)"
            :class="[
              item.current
                ? 'border-default text-default'
                : 'border-transparent text-secondary hover:border-default hover:text-default',
              'whitespace-nowrap border-b-4 py-4 px-4 text-sm font-medium',
            ]"
            :aria-current="item.current ? 'page' : undefined"
            >{{ item.name }}</a
          >
        </nav>
      </div>
    </div>
  </div>
</template>
<style>
/* CSS to disable page scrolling */
.no-scroll {
  overflow: hidden;
  height: 100vh;
}
</style>
<script setup lang="ts">
import { NavigationItem, NavigationCallback } from "../../types/index";

interface NavigationProps {
  show: boolean;
  navigationItems: NavigationItem[];
  currentNavigationItem?: NavigationItem;
  navigationCallback: NavigationCallback;
}

// onMounted(() => {
//   notificationStore.fetchMissedNotifications();
//   console.log("hello from navigation notification")
// });

const props = defineProps<NavigationProps>();
</script>
