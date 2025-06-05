<template>
  <div>
    <div v-if="isRoot" class="ml-[10px] p-[8px] mt-[2rem]">
      <div
        class="centered-column p-well space-y-well bg-accent rounded-md border border-default"
      >
        <div class="text-center mb-6">
          <h2 class="text-2xl font-bold text-default">Users with 2FA Enabled</h2>
        </div>

        <div class="flex justify-end mb-[4rem]">
          <button
            class="btn btn-danger"
            @click="confirmRemoveAll"
            :disabled="usersWith2FA.length === 0"
          >
            Remove 2FA for All Users
          </button>
        </div>

        <ul v-if="usersWith2FA.length > 0" class="space-y-4">
          <li
            v-for="user in usersWith2FA"
            :key="user"
            class="flex justify-between items-center p-4 border rounded shadow"
          >
            <span class="text-default font-semibold">{{ user }}</span>
            <button class="btn btn-danger" @click="confirmRemove(user)">
              Remove 2FA
            </button>
          </li>
        </ul>

        <p v-else class="text-center text-default">No users have 2FA enabled.</p>
      </div>

      <alertModal
        :show="showModal"
        :title="modalTitle"
        :confirmButtonText="confirmText"
        :message="modalMessage"
        @confirm="handleConfirm"
      />
    </div>

    <div v-else class="text-center text-red-600 mt-[4rem] text-lg font-semibold">
      ❌ You must be root to access this section.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Command, server } from "@45drives/houston-common-lib";
import { confirm } from "@45drives/houston-common-ui";
import alertModal from "../modal/alertModal.vue";

const usersWith2FA = ref<string[]>([]);
const modalTitle = ref("");
const modalMessage = ref("");
const confirmText = ref("OK");
const showModal = ref(false);

// Fetch users with .google_authenticator files on mount
const isRoot = ref(false);

onMounted(async () => {
  try {
    const result = await server.execute(new Command(["whoami"]), true);
    const user = new TextDecoder().decode(result.value.stdout).trim();
    isRoot.value = user === "root";
    if (isRoot.value) {
      await fetchUsersWith2FA();
    }
  } catch (error) {
    console.error("Error checking current user:", error);
    isRoot.value = false;
  }
});

async function fetchUsersWith2FA() {
  try {
    const result = await server.execute(
      new Command([
        "bash",
        "-c",
        `
        for user in $(awk -F: '$3 >= 1000 { print $1 }' /etc/passwd); do
          if [ -f /home/$user/.google_authenticator ]; then echo $user; fi
        done
        if [ -f /root/.google_authenticator ]; then echo root; fi
        `,
      ]),
      true
    );
    const output = new TextDecoder().decode(result.value.stdout).trim();
    usersWith2FA.value = output.split("\n").filter(Boolean);
  } catch (error) {
    console.error("Failed to fetch 2FA users:", error);
  }
}

async function confirmRemove(user: string) {
  const proceed = await confirm({
    body: `Are you sure you want to remove 2FA for user: ${user}?`,
    header: "Remove 2FA",
    confirmButtonText: "Yes",
    cancelButtonText: "Cancel",
  }).unwrapOr(false);
  if (proceed) {
    await remove2FA(user);
  }
}

async function remove2FA(user: string) {
  try {
    const homeDir = user === "root" ? "/root" : `/home/${user}`;
    await server.execute(
      new Command(["sh", "-c", `rm -f ${homeDir}/.google_authenticator`]),
      true
    );
    modalTitle.value = "✅ 2FA Removed";
    modalMessage.value = `2FA has been removed for user: ${user}`;
    showModal.value = true;
    const actorResult = await server.execute(new Command(["whoami"]), true);
    const actor = new TextDecoder().decode(actorResult.value.stdout).trim();

    await server.execute(
      new Command([
        "sh",
        "-c",
        `rm -f ${homeDir}/.google_authenticator && /opt/45drives/houston/2fa/scripts/log_2fa_removal.sh ${user} ${actor}`,
      ]),
      true
    );

    await fetchUsersWith2FA();
  } catch (error) {
    modalTitle.value = "❌ Error";
    modalMessage.value = `Failed to remove 2FA for ${user}`;
    showModal.value = true;
    console.error(error);
  }
}

async function confirmRemoveAll() {
  const proceed = await confirm({
    body: `This will remove 2FA for all users listed.\nDo you want to proceed?`,
    header: "Remove 2FA for All",
    confirmButtonText: "Yes, remove all",
    cancelButtonText: "Cancel",
  }).unwrapOr(false);

  if (proceed) {
    await remove2FAForAll();
  }
}

async function remove2FAForAll() {
  try {
    for (const user of usersWith2FA.value) {
      const homeDir = user === "root" ? "/root" : `/home/${user}`;
      await server.execute(
        new Command(["sh", "-c", `rm -f ${homeDir}/.google_authenticator`]),
        true
      );
    }
    modalTitle.value = "✅ All 2FA Removed";
    modalMessage.value = "2FA has been removed for all listed users.";
    showModal.value = true;
    await fetchUsersWith2FA();
  } catch (error) {
    modalTitle.value = "❌ Error";
    modalMessage.value = "Failed to remove 2FA for all users.";
    showModal.value = true;
    console.error("Bulk removal failed:", error);
  }
}

function handleConfirm() {
  showModal.value = false;
}
</script>
