<template>
  <div class="">
    <!-- Correct prop passing using v-slot -->
    <div>
      <div v-if="props.tag === 'my2Fa'" class="p-2">
        <MultiFactor></MultiFactor>
      </div>
      <div v-if="props.tag === 'userManagement'" class="p-2">
        <UserManagement></UserManagement>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import MultiFactor from "../components/multiFactor/MultiFactor.vue";
import UserManagement from "../components/userManagement/UserManagement.vue";

const preConfigurationComponent = ref();

interface Props {
  tag: string;
}

const props = defineProps<Props>();

// const loadpreConfigurationComponent = async () => {
//   const module = await import("../components/multiFactor/MultiFactor.vue");
//   preConfigurationComponent.value = module.default;
// };

// const userManagementComponent = ref();

// const loaduserManagement = async () => {
//   const module = await import("../components/userManagement/UserManagement.vue");
//   userManagementComponent.value = module.default;
// };
</script>
