<template>
  <div v-if="checkingRoot" class="flex justify-center items-center h-[60vh]">
    <LoadingSpinner class="w-24 h-24"></LoadingSpinner>
  </div>
  <div v-if="!checkingRoot">
    <div v-if="isRoot" class="ml-[10px] p-[8px] mt-[2rem]">
      <div
        class="centered-column p-well space-y-well bg-accent rounded-md border border-default"
      >
        <!-- ✅ USERS WITH 2FA ENABLED -->
        <div class="border rounded-md p-6 mb-[5rem] shadow-inner">
          <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-default">✅ Users with 2FA Enabled</h2>
            <p class="text-green-600 text-sm mt-2">
              These users have completed 2FA setup.
            </p>
          </div>

          <div class="flex justify-between items-center mb-6">
            <div>
              <input
                type="checkbox"
                id="selectAll"
                v-model="selectAll"
                @change="toggleSelectAll"
                class="mr-2"
              />
              <label for="selectAll" class="text-default font-medium">Select All</label>
            </div>

            <div class="space-x-4">
              <button
                class="btn bg-red-600 hover:bg-red-700 text-white"
                :disabled="selectedUsers.length === 0"
                @click="confirmRemoveSelected"
              >
                Remove Selected
              </button>
              <button
                class="btn bg-red-600 hover:bg-red-700 text-white"
                @click="confirmRemoveAll"
                :disabled="usersWith2FA.length === 0"
              >
                Remove 2FA for All Users
              </button>
            </div>
          </div>

          <ul v-if="usersWith2FA.length > 0" class="mt-[2rem]">
            <li
              v-for="user in usersWith2FA"
              :key="user"
              class="flex justify-between items-center py-4 px-2 border-b"
            >
              <div class="flex items-center">
                <input
                  type="checkbox"
                  :value="user"
                  v-model="selectedUsers"
                  class="mr-4"
                />
                <span class="text-default font-semibold">{{ user }}</span>
              </div>
              <button
                class="btn bg-red-600 hover:bg-red-700 text-white"
                @click="confirmRemove(user)"
              >
                Remove 2FA
              </button>
            </li>
          </ul>
          <p v-else class="text-center text-red-600">
            No users currently have 2FA enabled.
          </p>
        </div>

        <!-- ❌ USERS WITHOUT 2FA -->
        <div class="border rounded-md p-6 shadow-inner">
          <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-default">⚠️ Users Without 2FA</h2>
            <p class="text-yellow-600 text-sm mt-2">
              These users have not yet enabled 2FA.
            </p>
          </div>

          <ul v-if="usersWithout2FA.length > 0" class="space-y-4">
            <li
              v-for="user in usersWithout2FA"
              :key="user"
              class="p-4 border-b shadow text-default font-medium"
            >
              {{ user }}
            </li>
          </ul>

          <p v-else class="text-center text-green-600">All users have 2FA enabled.</p>
        </div>
      </div>

      <!-- Confirmation Modal -->
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
import { ref, onMounted, watch } from "vue";
import { Command, server } from "@45drives/houston-common-lib";
import { confirm, LoadingSpinner } from "@45drives/houston-common-ui";
import alertModal from "../modal/alertModal.vue";
import {
  modalTitle,
  modalMessage,
  confirmText,
  showModal,
  reset2FAState,
} from "../../types/index";
const selectedUsers = ref<string[]>([]);
const selectAll = ref(false);
// Fetch users with .google_authenticator files on mount
const isRoot = ref(false);
const checkingRoot = ref(true);
const usersWith2FA = ref<string[]>([]);
const usersWithout2FA = ref<string[]>([]);

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
  } finally {
    checkingRoot.value = false;
  }
});
async function fetchUsersWith2FA() {
  try {
    const result = await server.execute(
      new Command([
        "bash",
        "-c",
        `
        all_users=$(awk -F: '$3 >= 1000 { print $1 }' /etc/passwd)
        with_2fa=()
        without_2fa=()

        for user in $all_users; do
          if [ -f /home/$user/.google_authenticator ]; then
            with_2fa+=($user)
          else
            without_2fa+=($user)
          fi
        done

        if [ -f /root/.google_authenticator ]; then
          with_2fa+=("root")
        else
          without_2fa+=("root")
        fi

        echo "WITH_2FA:\${with_2fa[*]}"
        echo "WITHOUT_2FA:\${without_2fa[*]}"
        `,
      ]),
      true
    );

    const output = new TextDecoder().decode(result.value.stdout).trim();
    const lines = output.split("\n");

    const withLine = lines.find((line) => line.startsWith("WITH_2FA:")) || "";
    const withoutLine = lines.find((line) => line.startsWith("WITHOUT_2FA:")) || "";

    usersWith2FA.value = withLine
      .replace("WITH_2FA:", "")
      .trim()
      .split(/\s+/)
      .filter(Boolean);
    usersWithout2FA.value = withoutLine
      .replace("WITHOUT_2FA:", "")
      .trim()
      .split(/\s+/)
      .filter(Boolean);
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

    // Remove the file
    await server.execute(
      new Command(["sh", "-c", `rm -f ${homeDir}/.google_authenticator`]),
      true
    );

    // Set UI state
    modalTitle.value = "✅ 2FA Removed";
    modalMessage.value = `2FA has been removed for user: ${user}`;
    showModal.value = true;

    // Log the actor
    const actorResult = await server.execute(new Command(["whoami"]), true);
    const actor = new TextDecoder().decode(actorResult.value.stdout).trim();

    // Log the removal
    await server.execute(
      new Command([
        "sh",
        "-c",
        `/opt/45drives/houston/2fa/scripts/log_2fa_removal.sh ${user} ${actor}`,
      ]),
      true
    );

    // If the removed user is root, reset shared UI state
    if (user === "root") {
      reset2FAState();
    }

    // Refresh user list
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
    reset2FAState();
  }
}

async function remove2FAForAll() {
  try {
    const actorResult = await server.execute(new Command(["whoami"]), true);
    const actor = new TextDecoder().decode(actorResult.value.stdout).trim();

    for (const user of usersWith2FA.value) {
      const homeDir = user === "root" ? "/root" : `/home/${user}`;
      await server.execute(
        new Command([
          "sh",
          "-c",
          `rm -f ${homeDir}/.google_authenticator && /opt/45drives/houston/2fa/scripts/log_2fa_removal.sh ${user} ${actor}`,
        ]),
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

function toggleSelectAll() {
  if (selectAll.value) {
    selectedUsers.value = [...usersWith2FA.value];
  } else {
    selectedUsers.value = [];
  }
}

async function confirmRemoveSelected() {
  const proceed = await confirm({
    body: `Remove 2FA for the selected users: ${selectedUsers.value.join(", ")}?`,
    header: "Confirm Bulk Removal",
    confirmButtonText: "Yes, remove",
    cancelButtonText: "Cancel",
  }).unwrapOr(false);

  if (proceed) {
    await remove2FAForSelected();
  }
}

async function remove2FAForSelected() {
  try {
    const actorResult = await server.execute(new Command(["whoami"]), true);
    const actor = new TextDecoder().decode(actorResult.value.stdout).trim();

    for (const user of selectedUsers.value) {
      const homeDir = user === "root" ? "/root" : `/home/${user}`;
      await server.execute(
        new Command([
          "sh",
          "-c",
          `rm -f ${homeDir}/.google_authenticator && /opt/45drives/houston/2fa/scripts/log_2fa_removal.sh ${user} ${actor}`,
        ]),
        true
      );
    }

    modalTitle.value = "✅ 2FA Removed";
    modalMessage.value = `2FA removed for selected users.`;
    showModal.value = true;
    selectedUsers.value = [];
    selectAll.value = false;
    await fetchUsersWith2FA();
  } catch (error) {
    modalTitle.value = "❌ Error";
    modalMessage.value = `Failed to remove 2FA for selected users.`;
    showModal.value = true;
    console.error("Error in batch removal:", error);
  }
}

watch([selectedUsers, usersWith2FA], () => {
  // If all users are selected, set selectAll to true; otherwise, false
  const allSelected =
    usersWith2FA.value.length > 0 &&
    selectedUsers.value.length === usersWith2FA.value.length &&
    usersWith2FA.value.every((user) => selectedUsers.value.includes(user));

  selectAll.value = allSelected;
});

function handleConfirm() {
  showModal.value = false;
}
</script>
