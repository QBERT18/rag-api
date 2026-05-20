<template>
  <div class="flex h-screen bg-white text-slate-900">
    <aside class="flex w-1/3 min-w-[280px] max-w-md flex-col border-r border-slate-200">
      <div class="min-h-0 flex-1 border-b border-slate-200">
        <ChatList />
      </div>
      <div class="h-2/5 min-h-[180px]">
        <DocumentsPane />
      </div>
    </aside>
    <main class="flex-1">
      <ChatPane />
    </main>
  </div>
</template>
