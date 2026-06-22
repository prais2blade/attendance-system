import { useState } from "react";

import DashboardLayout from "../components/layout/DashboardLayout";

import { useStudents } from "../hooks/useStudents";

export default function Students() {

    const {

        data: students = []

    } = useStudents();

    const [

        search,

        setSearch

    ] = useState("");

    const filteredStudents = students.filter(

        student =>

            (
                student.first_name +
                " " +
                student.last_name
            )

            .toLowerCase()

            .includes(

                search.toLowerCase()

            )

    );

    return (

        <DashboardLayout>

            <div className="flex justify-between items-center mb-6">

                <h1 className="text-3xl font-bold">

                    Students

                </h1>

                <input

                    type="text"

                    placeholder="Search student..."

                    value={search}

                    onChange={(e) =>

                        setSearch(
                            e.target.value
                        )

                    }

                    className="
                        bg-slate-900
                        border
                        border-slate-700
                        rounded-lg
                        px-4
                        py-2
                    "

                />

            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">

                {filteredStudents.map(

                    student => (

                        <div

                            key={
                                student.student_id
                            }

                            className="
                                bg-slate-900
                                rounded-xl
                                p-5
                            "

                        >

                            <div className="flex items-center gap-4">

                                {student.photo ? (

                                    <img

                                        src={student.photo}

                                        alt="student"

                                        className="
                                            h-16
                                            w-16
                                            rounded-full
                                            object-cover
                                        "

                                    />

                                ) : (

                                    <div className="h-16 w-16 rounded-full bg-slate-700">

                                    </div>

                                )}

                                <div>

                                    <h3 className="font-semibold">

                                        {student.first_name}
                                        {" "}
                                        {student.last_name}

                                    </h3>

                                    <p className="text-sm text-slate-400">

                                        {student.student_id}

                                    </p>

                                </div>

                            </div>

                            <div className="mt-4 text-sm">

                                <p>

                                    Class:
                                    {" "}
                                    {student.class_name}

                                </p>

                                <p>

                                    Parent:
                                    {" "}
                                    {student.parent_name}

                                </p>

                            </div>

                        </div>

                    )

                )}

            </div>

        </DashboardLayout>

    );

}