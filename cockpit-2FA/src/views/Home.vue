<template>
  <div class="w-full h-dvh min-h-dvh overflow-visible bg-default text-default">
    <!-- Correct prop passing using v-slot -->
    <div>
      <PreConfiguration></PreConfiguration>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import PreConfiguration from "../components/preConfiguration/PreConfiguration.vue";




</script>
