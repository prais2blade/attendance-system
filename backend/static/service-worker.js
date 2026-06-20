const CACHE_NAME = "attendance-v1";

const urlsToCache = [

    "/",

    "/students/",

    "/api/attendance/dashboard/",

    "/api/attendance/reports/"

];

self.addEventListener(

    "install",

    event => {

        event.waitUntil(

            caches.open(CACHE_NAME)

            .then(cache => {

                return cache.addAll(
                    urlsToCache
                );

            })

        );

    }

);

self.addEventListener(

    "fetch",

    event => {

        event.respondWith(

            caches.match(
                event.request
            )

            .then(response => {

                return (
                    response ||

                    fetch(
                        event.request
                    )

                );

            })

        );

    }

);