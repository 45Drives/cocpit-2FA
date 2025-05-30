<template>
  <div class="mt-[5rem]">
    <div class="ml-[10px] p-[8px]" data-step-content-idx="0">
      <div
        class="min-w-full max-w-full max-h-full py-2 pb-4 align-middle sm:px-4 lg:px-6 sm:rounded-lg bg-accent rounded-md border border-default">
        <div
          class="flex flex-row bg-well text-center items-center rounded-md shadow text-default my-2 rounded-b-md ring-1 ring-black ring-opacity-5">
          <h1 class="panel-title cd-row-child text-2xl">
            Set up 2FA
          </h1>
        </div>

        <div v-if="codeGenrated" class="text-lg">
        <p>Your account has been set up for 2FA, to remove 2FA click on Remove button</p>
        <br>
        <p>To reset, first remove it </p>

        <button class="btn btn-primary" @click="confirmRemove()">Remove 2FA</button>

      </div>

        <div  v-else>
        <div class="text-lg">
          <p class="font-bold p-[1em]">
            To enhance your account's security, enable Two-Factor Authentication (2FA).
          </p>

          <p class="p-[1em]">
            First, install the <strong>Google Authenticator</strong> app on your phone:
            <a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2"
              target="_blank" class="text-primary underline">Google Play</a> |
            <a href="https://apps.apple.com/app/google-authenticator/id388497605" target="_blank"
              class="text-primary underline">App Store</a>
          </p>

          <p class="p-[1em]">
            Once the app is installed, click the <strong>"Generate QR Code"</strong> button below
            and scan the code using the Google Authenticator app to complete setup.
          </p>
        </div>
        <div class="flex flex-row items-start justify-center space-x-12 mt-6">
        <div>
          <qrcode-vue v-if="otpUri.length > 0" :value="otpUri" :size="400" />

          <button  v-if="!codeGenrated" class="btn btn-primary" @click="createAuth()">Generate QR Code</button>

        </div>
            <div v-if="scratchCodes.length > 0">
          <p class="font-bold mt-4 text-lg">Emergency Scratch Codes</p>
          <p class="text-sm mb-2">Please save these in a secure place. They can be used if you lose access to your
            authenticator app.</p>
          <ul class="list-disc list-inside text-default">
            <li v-for="(code, index) in scratchCodes" :key="index" class="text-accent font-mono">
              {{ code }}
            </li>
          </ul>
        </div>
        </div>

      </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import QrcodeVue from "qrcode.vue";
import { Command, legacy } from "@45drives/houston-common-lib";
import { onMounted, ref } from "vue";
import { server } from "@45drives/houston-common-lib";

const otpUri = ref("");
const secret = ref("");
const scratchCodes = ref<string[]>([]);
const codeGenrated = ref(false)

onMounted(() => {
  checkExist()
})

async function checkExist() {
  try {
    const result = await server.execute(
      new Command(["cat", "/root/.google_authenticator"]),
      true
    );

    const output = result.value.getStdout().trim(); // Trim to remove newlines/spaces
    if (output.length > 0) {
      codeGenrated.value = true
      console.log(" File exists and contains content");
      return true;
    } else {
      codeGenrated.value = false

      console.warn("⚠️ File is empty or does not contain useful data");
      return false;
    }
  } catch (error) {
    codeGenrated.value = false

    console.error("❌ Failed to read .google_authenticator file:", error);
    return false;
  }
}


async function createAuth() {
  try {
    const result = await server.execute(
      new Command([
        "google-authenticator",
        "--time-based",
        "--disallow-reuse",
        "--rate-limit=3",
        "--rate-time=30",
        "--window-size=17",
        "--no-confirm",
        "--force"
      ]),
      true
    );
    // Decode Uint8Array to string
    const stdoutBytes = result.value.stdout;
    const stdout = new TextDecoder().decode(stdoutBytes);
    console.log("Decoded output:", stdout);

    // Extract QR URL
    const qrMatch = stdout.match(
      /https:\/\/www\.google\.com\/chart\?chs=200x200[^ \n"]+/
    );
    const qrUrl = qrMatch?.[0] ?? null;

    if (qrUrl) {
      // Extract the otpauth URI from the 'chl' parameter
      const chlMatch = qrUrl.match(/chl=([^&\n]+)/);
      const encodedOtpauth = chlMatch?.[1];

      if (encodedOtpauth) {
        // Decode it
        const otpauthUri = decodeURIComponent(encodedOtpauth);
        console.log("✅ OTP Auth URI:", otpauthUri);

        // Example: use in UI
        otpUri.value = otpauthUri;
      } else {
        console.warn("⚠️ Couldn't find 'chl=' param in QR URL");
      }
    } else {
      console.error("❌ QR URL not found in stdout");
    }
    server
      .execute(new Command(["cat", "/root/.google_authenticator"]), true)
      .map((proc) => {
        const lines = proc.getStdout().split("\n");
        console.log("lines", lines)
        secret.value = lines[0]?.trim(); // ✅ Save secret separately
        scratchCodes.value.push(...lines.filter((line) => /^\d{8}$/.test(line.trim())));
      });
  } catch (e) {

    console.error("Failed to generate OTP:", e);
    return null;
  }
}

function confirmRemove() {
  if (confirm("Are you sure you want to remove 2FA for this account?")) {
    remove2FA();
  }
}

async function remove2FA(){

  const result = await server.execute(
      new Command(["rm", "-f", "/root/.google_authenticator"]
      ),
      true
    );
    codeGenrated.value = false;
}
</script>
