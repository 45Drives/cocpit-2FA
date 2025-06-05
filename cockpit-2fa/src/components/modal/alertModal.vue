<template>
  <Modal :show="show">
    <CardContainer class="w-[50rem] p-6 space-y-4">
      <!-- Header -->
      <template #header>
        <h2 class="text-lg font-semibold text-center text-default">{{ title }}</h2>
      </template>

      <!-- Message Body -->
      <div class="text-base text-default leading-relaxed whitespace-pre-line">
        {{ message }}
      </div>

      <!-- Footer -->
      <template #footer>
        <div class="flex justify-end">
          <button
            class="btn btn-primary px-5 py-2 rounded-md text-sm font-medium"
            @click="$emit('confirm')"
          >
            {{ confirmButtonText || "Confirm" }}
          </button>
        </div>
      </template>
    </CardContainer>
  </Modal>
</template>

<script setup lang="ts">
import { CardContainer, Modal } from "@45drives/houston-common-ui";

defineProps<{
  show: boolean;
  title: string;
  message: string;
  confirmButtonText?: string;
}>();
defineEmits(["confirm"]);
</script>
