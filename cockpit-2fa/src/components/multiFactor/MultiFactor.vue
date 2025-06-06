<template>
  <div>
    <div class="ml-[10px] p-[8px] mt-[2rem]" data-step-content-idx="0">
      <div
        class="centered-column p-well space-y-well bg-accent rounded-md border border-default"
      >
        <div v-if="loaded">
          <div
            v-if="codeGenrated"
            class="text-lg flex flex-col items-center justify-center text-center p-6"
          >
            <p class="mb-2 font-bold">
              Your account has been set up for 2FA. To remove 2FA, click on the button
              below.
            </p>
            <p class="mb-4 text-base">To reset 2FA, you must remove it first.</p>
            <div class="text-center">
              <button
                class="bg-red-600 hover:bg-red-700 mt-[2rem] text-white font-semibold py-2 px-4 rounded shadow"
                @click="confirmRemove()"
              >
                Remove 2FA
              </button>
            </div>
          </div>

          <div v-else>
            <div class="text-center">
              <h2 class="text-2xl font-bold text-default">
                Secure Your Account with Two-Factor Authentication (2FA)
              </h2>
              <p class="mt-2 text-default text-base">
                To get started, install the <strong>Google Authenticator</strong> app on
                your phone:
                <br />
                <a
                  href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2"
                  target="_blank"
                  class="text-blue-500 underline hover:text-blue-700"
                  >Google Play</a
                >
                |
                <a
                  href="https://apps.apple.com/app/google-authenticator/id388497605"
                  target="_blank"
                  class="text-blue-500 underline hover:text-blue-700"
                  >App Store</a
                >
              </p>
            </div>

            <div class="text-center text-default">
              <p class="text-base">
                Once the app is installed, click
                <strong>"Generate QR Code"</strong> below to begin setup.
              </p>
            </div>

            <div
              class="flex flex-col lg:flex-row justify-center items-start gap-12 mt-[5rem]"
            >
              <!-- QR and input -->
              <div class="flex flex-col items-center space-y-4">
                <qrcode-vue
                  v-if="otpUri.length > 0"
                  :value="otpUri"
                  :size="250"
                  class="border-2 border-gray-300 p-2 rounded"
                />

                <div v-if="generateQrBtnClicked" class="text-center space-y-3">
                  <p class="text-bash font-semibold">Can’t scan the QR code?</p>
                  <p class="text-sm text-default">Enter this info manually in the app:</p>

                  <p class="text-sm"><strong>Account:</strong> {{ accountName }}</p>
                  <p class="text-sm break-all font-mono ml-[5rem]">
                    <strong>Key:</strong> {{ secret }}
                  </p>
                  <p class="text-sm">Set type to <strong>Time-based</strong></p>
                </div>

                <div v-if="!generateQrBtnClicked">
                  <button class="btn btn-primary" @click="createAuth()">
                    Generate QR Code
                  </button>
                </div>
                <div v-if="generateQrBtnClicked" class="text-center mt-6">
                  <p class="font-medium">
                    Enter the 6-digit code from your Authenticator app:
                  </p>
                  <input
                    v-model="userInput"
                    type="text"
                    maxlength="6"
                    placeholder="123456"
                    class="mt-2 px-4 py-2 w-40 border mr-[1rem] bg-default border-gray-300 rounded text-center font-mono text-lg tracking-widest"
                  />
                  <button @click="verifyCode(userInput)" class="btn btn-primary mt-4">
                    Verify & Finalize 2FA
                  </button>
                </div>
              </div>
              <!-- Scratch Codes -->
              <div v-if="scratchCodes.length > 0" class="max-w-md w-full">
                <p class="font-bold text-lg mb-2">Emergency Scratch Codes</p>
                <p class="text-bash mb-4">
                  Store these codes in a safe place. Each code can be used once if you
                  lose access to your device.
                </p>
                <ul class="grid grid-cols-2 gap-3 text-red-600 font-mono text-base">
                  <li
                    v-for="(code, index) in scratchCodes"
                    :key="index"
                    class="bg-white border rounded p-2 text-center"
                  >
                    {{ code }}
                  </li>
                </ul>
                <div class="text-center">
                  <button
                    class="bg-red-600 hover:bg-red-700 mt-[2rem] text-white font-semibold py-2 px-4 rounded shadow"
                    @click="confirmRemove()"
                  >
                    Remove 2FA
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <alertModal
        :show="showModal"
        :title="modalTitle"
        :confirmButtonText="confirmText"
        :message="modalMessage"
        @confirm="handleConfirm"
      ></alertModal>
    </div>
  </div>
</template>

<script setup lang="ts">
import QrcodeVue from "qrcode.vue";
import { Command, legacy } from "@45drives/houston-common-lib";
import { onMounted, ref } from "vue";
import { server } from "@45drives/houston-common-lib";
import { confirm } from "@45drives/houston-common-ui";
import alertModal from "../modal/alertModal.vue";
import {
  otpUri,
  secret,
  scratchCodes,
  codeGenrated,
  generateQrBtnClicked,
  userInput,
  accountName,
  modalTitle,
  modalMessage,
  confirmText,
  showModal,
  fileGenerated,
  verified,
  reset2FAState,
} from "../../types/index";
// const otpUri = ref("");
// const secret = ref("");
// const scratchCodes = ref<string[]>([]);
// const codeGenrated = ref(false);
const loaded = ref(false);
// const generateQrBtnClicked = ref(false);
// const userInput = ref("");
// const accountName = ref("");
// const modalTitle = ref("Default Title");
// const modalMessage = ref("Default message.");
// const confirmText = ref("Continue");
// const showModal = ref(false);
// const fileGenerated = ref(false);
// const verified = ref(false);

checkExist().then(() => {
  loaded.value = true;
});

async function checkExist() {
  try {
    const result = await server.execute(
      new Command([
        "sh",
        "-c",
        "test -f ~/.google_authenticator && cat ~/.google_authenticator || echo ''",
      ]),
      true
    );

    const stdout = new TextDecoder().decode(result.value.stdout).trim();

    if (stdout.length > 0) {
      codeGenrated.value = true;
      console.log("✅ .google_authenticator file exists and has content.");
      return true;
    } else {
      codeGenrated.value = false;
      console.warn("⚠️ .google_authenticator file does not exist or is empty.");
      return false;
    }
  } catch (error) {
    // Only log truly unexpected errors
    console.error("❌ Unexpected error checking .google_authenticator:", error);
    codeGenrated.value = false;
    return false;
  }
}

async function generateFile() {
  const result = await server.execute(
    new Command([
      "python3",
      "/opt/45drives/houston/2fa/scripts/generateAuthFIle.py",
      secret.value,
    ]),
    true
  );

  const stdout = new TextDecoder().decode(result.value.stdout).trim();
  const res = JSON.parse(stdout);

  if (res.status === "success") {
    scratchCodes.value = res.scratch_codes;
    fileGenerated.value = true;

    // alert("✅ 2FA enabled. Save your recovery codes.");
  } else {
    const proceed = await confirm({
      body: " Failed to Enable 2FA",
      header: "❌ 2FA Failed.",
      confirmButtonText: "Ok",
    }).unwrapOr(false);
    // alert("❌ Failed: " + res.message);
  }
}

async function verifyCode(userInput) {
  try {
    const result = await server.execute(
      new Command([
        "python3",
        "/opt/45drives/houston/2fa/scripts/verifyCode.py",
        userInput,
        secret.value,
      ]),
      true
    );

    const stdout = new TextDecoder().decode(result.value.stdout).trim();
    console.log("result", stdout);

    // Try parsing JSON output from the script
    const res = JSON.parse(stdout);

    if (res.status === "valid") {
      verified.value = true;
      // ✅ TOTP is correct
      modalTitle.value = "✅ Verified";
      modalMessage.value =
        "Two-Factor Authentication has been successfully enabled.\n\nYou will now be shown your one-time recovery codes.\nPlease save them immediately — they will not be shown again.";
      confirmText.value = "Ok";
      showModal.value = true;

      // TODO: call backend to save `.google_authenticator` file or mark setup complete
    } else if (res.status === "invalid") {
      modalTitle.value = "❌ Invalid code";
      modalMessage.value = "Invalid 2FA code. Please try again.";
      confirmText.value = "Ok";
      showModal.value = true;
    } else {
      modalTitle.value = "⚠️ Verification error: ";
      modalMessage.value = "⚠️ Verification error: " + (res.message || "Unknown issue.");
      confirmText.value = "Ok";
      showModal.value = true;
    }
  } catch (error) {
    modalTitle.value = "❌ Error verifying TOTP:";
    (modalMessage.value = " Error verifying TOTP:"), error;
    confirmText.value = "Ok";
    showModal.value = true;
    console.error("❌ Error verifying TOTP:", error);
  }
}

async function createAuth() {
  try {
    const result = await server.execute(
      new Command(["python3", "/opt/45drives/houston/2fa/scripts/generateUri.py"]),
      true
    );
    const stdout = new TextDecoder().decode(result.value.stdout);
    console.log("result", stdout);
    const json = JSON.parse(stdout);

    // Access the parsed values
    otpUri.value = json.otpauth_uri;
    secret.value = json.secret;
    accountName.value = json.account;
    generateQrBtnClicked.value = true;
  } catch (e) {
    console.error("❌ Failed to generate OTP:", e);
  }
}

function handleConfirm() {
  console.log("Confirmed:", modalTitle.value);
  showModal.value = false;
  if (verified.value && !fileGenerated.value) {
    console.log("🚀 Generating file after user clicked OK");
    generateFile();
  }
  verified.value = false;
}

async function confirmRemove() {
  const proceed = await confirm({
    body: "Are you sure you want to remove 2FA for this account?",
    header: "Remove 2FA",
    confirmButtonText: "Yes",
    cancelButtonText: "Cancel",
  }).unwrapOr(false);
  if (proceed) {
    remove2FA();
  }
}

async function remove2FA() {
  const result = await server.execute(
    new Command(["sh", "-c", "rm -f ~/.google_authenticator"]),
    true
  );
  reset2FAState();
}
</script>
